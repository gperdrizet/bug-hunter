"""
3-pass LLM generation pipeline with server-side subprocess verification.

Pass 1: Generate working Python snippet
Pass 2: Generate test cases, verify working code passes all of them
Pass 3: Generate broken version, verify it fails at least one test
"""
import asyncio
import json
import logging
import re
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

from app.llm.providers import LLMProvider, get_provider
from app.models import Difficulty, Topic
from app.pipeline.examples import sample_examples

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
SUBPROCESS_TIMEOUT = 10  # seconds


# ---------------------------------------------------------------------------
# Subprocess verification helpers
# ---------------------------------------------------------------------------

def _run_code(code: str) -> tuple[bool, str]:
    """Run Python code in a subprocess. Returns (success, output)."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        tmp_path = f.name
    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT,
        )
        output = result.stdout + result.stderr
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "Timed out"
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def _build_test_harness(working_code: str, test_cases: list[dict]) -> str:
    """Wrap working code + test cases into a runnable script that exits non-zero on failure."""
    tests_code = []
    for i, tc in enumerate(test_cases):
        tests_code.append(f"# Test {i + 1}: {tc.get('name', '')}")
        tests_code.append(tc["code"])
    return working_code + "\n\n" + "\n".join(tests_code)


def _extract_code_block(text: str) -> str:
    """Pull code out of markdown fences if present."""
    match = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def _extract_json(text: str) -> list:
    """Extract a JSON array from LLM output."""
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    return json.loads(text.strip())


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

PASS1_PROMPT = """You are generating Python code for an educational bug-fixing platform.

Topic: {topic}
Difficulty: {difficulty}

{examples_section}Write a concise Python code snippet (10–30 lines) that:
1. Clearly demonstrates the topic and ONLY the topic — every function must be directly related to it
2. Is appropriate for the difficulty level (easy = beginner, medium = intermediate, hard = advanced)
3. Defines one primary function (plus helper functions only if they directly support it) that can be tested with specific inputs and expected outputs
4. Is complete and correct — it must run without errors

Important: do NOT include unrelated functions. A snippet about multiplication must not contain string-formatting, greeting, or other unrelated logic. Keep the scope tight.

Return ONLY the Python code, no explanation, no markdown fences."""

PASS2_PROMPT = """You are generating test cases for an educational Python platform.

Here is a working Python snippet:

```python
{code}
```

Generate exactly 4 test cases that verify the code works correctly.
Each test case must:
- Call a function defined in the snippet with specific inputs
- Assert the result equals the expected output using `assert`
- Have a descriptive name as a comment

Return a JSON array with this exact structure:
[
  {{
    "name": "descriptive test name",
    "code": "assert function_name(arg) == expected_value, 'descriptive message'"
  }}
]

Return ONLY the JSON array, no markdown, no explanation."""

PASS3_PROMPT = """You are creating an educational debugging exercise.

Here is a working Python snippet:

```python
{code}
```

The test cases that verify it are:
{tests}

Introduce EXACTLY ONE bug into the code. The bug must either:
1. Cause a SyntaxError (code does not run at all)
2. Cause a RuntimeError/exception during execution
3. Cause incorrect output that fails at least one test case

The bug should be realistic — the kind a student might write by mistake (e.g., wrong operator, off-by-one, incorrect variable name, missing return, wrong comparison, wrong indentation).

Do NOT change function signatures or remove functions — the tests must be able to call the same functions.

Return ONLY the modified Python code, no explanation, no markdown fences."""


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

async def generate_snippet(
    topic: Topic,
    difficulty: Difficulty,
    provider: LLMProvider | None = None,
) -> dict:
    """
    Run the 3-pass generation pipeline.
    Returns a dict ready to be stored as a Snippet.
    Raises RuntimeError if all retries fail.
    """
    if provider is None:
        provider = get_provider()

    logger.info("[pipeline] starting generation: topic=%s difficulty=%s provider=%s", topic, difficulty, provider.provider_name)

    # ---- Pass 1: Working code ------------------------------------------------
    working_code = await _pass1_generate_working_code(provider, topic, difficulty)
    logger.info("[pipeline] pass 1 done (%d chars)", len(working_code))

    # ---- Pass 2: Test cases --------------------------------------------------
    test_cases = await _pass2_generate_tests(provider, working_code)
    logger.info("[pipeline] pass 2 done (%d test cases)", len(test_cases))

    # ---- Pass 3: Broken code -------------------------------------------------
    broken_code = await _pass3_generate_broken(provider, working_code, test_cases)
    logger.info("[pipeline] pass 3 done")

    # ---- Extract title from working code -------------------------------------
    title = _extract_title(working_code, topic, difficulty)

    return {
        "id": uuid.uuid4(),
        "topic": topic,
        "difficulty": difficulty,
        "title": title,
        "working_code": working_code,
        "broken_code": broken_code,
        "test_cases": test_cases,
        "llm_provider": provider.provider_name,
        "llm_model": provider.model_name,
    }


async def _pass1_generate_working_code(provider: LLMProvider, topic: Topic, difficulty: Difficulty) -> str:
    examples = sample_examples(topic, n=2)
    if examples:
        parts = ["For diversity, here are example snippets on this topic. "
                 "Write something with a DIFFERENT concept or approach than any of these:\n"]
        for i, ex in enumerate(examples, 1):
            parts.append(f"--- Example {i} ---\n```python\n{ex}```\n")
        parts.append("Your snippet MUST use a different algorithm, data structure, "
                     "or problem than the examples above.\n\n")
        examples_section = "\n".join(parts)
    else:
        examples_section = ""

    prompt = PASS1_PROMPT.format(
        topic=topic.value.replace("_", " "),
        difficulty=difficulty.value,
        examples_section=examples_section,
    )
    for attempt in range(MAX_RETRIES):
        raw = await provider.complete(prompt)
        code = _extract_code_block(raw)
        success, output = await asyncio.get_event_loop().run_in_executor(None, _run_code, code)
        if success:
            return code
        if attempt < MAX_RETRIES - 1:
            prompt = prompt + f"\n\nYour previous attempt failed with:\n{output}\n\nTry again."
    raise RuntimeError(f"Pass 1 failed after {MAX_RETRIES} attempts")


async def _pass2_generate_tests(provider: LLMProvider, working_code: str) -> list[dict]:
    prompt = PASS2_PROMPT.format(code=working_code)
    for attempt in range(MAX_RETRIES):
        raw = await provider.complete(prompt)
        try:
            test_cases = _extract_json(raw)
        except (json.JSONDecodeError, ValueError) as e:
            if attempt < MAX_RETRIES - 1:
                continue
            raise RuntimeError(f"Pass 2 JSON parse failed: {e}") from e

        harness = _build_test_harness(working_code, test_cases)
        success, output = await asyncio.get_event_loop().run_in_executor(None, _run_code, harness)
        if success:
            return test_cases
        if attempt < MAX_RETRIES - 1:
            prompt = PASS2_PROMPT.format(code=working_code) + f"\n\nPrevious tests failed:\n{output}\n\nFix the tests."
    raise RuntimeError(f"Pass 2 failed after {MAX_RETRIES} attempts")


async def _pass3_generate_broken(provider: LLMProvider, working_code: str, test_cases: list[dict]) -> str:
    tests_str = "\n".join(f"- {tc['name']}: {tc['code']}" for tc in test_cases)
    prompt = PASS3_PROMPT.format(code=working_code, tests=tests_str)
    for attempt in range(MAX_RETRIES):
        raw = await provider.complete(prompt)
        broken = _extract_code_block(raw)

        # Verify: broken code must fail (either exception or test failure)
        harness = _build_test_harness(broken, test_cases)
        success, _ = await asyncio.get_event_loop().run_in_executor(None, _run_code, harness)
        if not success:
            return broken
        if attempt < MAX_RETRIES - 1:
            prompt = PASS3_PROMPT.format(code=working_code, tests=tests_str) + \
                "\n\nYour previous broken version still passed all tests. Make a more impactful bug."
    raise RuntimeError(f"Pass 3 failed after {MAX_RETRIES} attempts")


def _extract_title(code: str, topic: Topic, difficulty: Difficulty) -> str:
    """Derive a title from the first function definition, falling back to topic+difficulty."""
    match = re.search(r"^def\s+(\w+)\s*\(", code, re.MULTILINE)
    if match:
        name = match.group(1).replace("_", " ").title()
        return f"{name} ({difficulty.value.capitalize()})"
    return f"{topic.value.replace('_', ' ').title()} — {difficulty.value.capitalize()}"
