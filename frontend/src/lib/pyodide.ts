import type { TestCase, TestResult } from "../types";

declare global {
  interface Window {
    loadPyodide: (config?: { stdout?: (msg: string) => void }) => Promise<PyodideInterface>;
  }
}

interface PyodideInterface {
  runPythonAsync: (code: string, options?: { globals?: unknown }) => Promise<unknown>;
  globals: {
    get: (key: string) => unknown;
    set: (key: string, value: unknown) => void;
    toJs: () => Map<string, unknown>;
  };
  toPy: (obj: unknown) => unknown;
  pyimport: (mod: string) => unknown;
}

let pyodideInstance: PyodideInterface | null = null;
let loadingPromise: Promise<PyodideInterface> | null = null;

const PYODIDE_VERSION = "0.27.6";
const PYODIDE_CDN = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/pyodide.js`;

export async function loadPyodide(): Promise<PyodideInterface> {
  if (pyodideInstance) return pyodideInstance;
  if (loadingPromise) return loadingPromise;

  loadingPromise = (async () => {
    // Inject the Pyodide loader script if not already present
    if (!document.getElementById("pyodide-script")) {
      await new Promise<void>((resolve, reject) => {
        const script = document.createElement("script");
        script.id = "pyodide-script";
        script.src = PYODIDE_CDN;
        script.onload = () => resolve();
        script.onerror = () => reject(new Error("Failed to load Pyodide script"));
        document.head.appendChild(script);
      });
    }

    const instance = await window.loadPyodide();
    pyodideInstance = instance;
    return instance;
  })();

  return loadingPromise;
}

export function isPyodideReady(): boolean {
  return pyodideInstance !== null;
}

/**
 * Run student code in-browser and capture stdout/stderr.
 * Does not run test cases.
 */
export async function runCode(studentCode: string): Promise<{ stdout: string; error: string | null }> {
  const pyodide = await loadPyodide();

  // Pass code as a global so compile() can assign a meaningful filename,
  // giving traceback line numbers that match what the student sees in the editor.
  pyodide.globals.set("_student_code", studentCode);

  const captureCode = `
import sys
import io
import contextlib
import traceback

_stdout_buf = io.StringIO()
_run_error = None

try:
    with contextlib.redirect_stdout(_stdout_buf):
        exec(compile(_student_code, "<student code>", "exec"), {"__name__": "__main__"})
except SystemExit:
    _run_error = "SystemExit raised"
except Exception:
    _run_error = traceback.format_exc()
`;

  try {
    await pyodide.runPythonAsync(captureCode);
    const stdout = (pyodide.globals.get("_stdout_buf") as { getvalue: () => string }).getvalue?.() ?? "";
    const error = pyodide.globals.get("_run_error") as string | null;
    return { stdout, error };
  } catch (e) {
    return { stdout: "", error: String(e) };
  }
}

/**
 * Run student code against test cases entirely in-browser.
 * Returns structured per-test results.
 */
export async function runTests(
  studentCode: string,
  testCases: TestCase[]
): Promise<TestResult[]> {
  const pyodide = await loadPyodide();
  const results: TestResult[] = [];

  for (const tc of testCases) {
    let passed = false;
    let stdout = "";
    let error: string | null = null;

    // Pass code via globals so compile() can use meaningful filenames in tracebacks.
    pyodide.globals.set("_student_code", studentCode);
    pyodide.globals.set("_test_code", tc.code);

    const captureCode = `
import sys
import io
import contextlib
import traceback

_stdout_buf = io.StringIO()
_result_passed = False
_result_error = None
_ns = {}

try:
    with contextlib.redirect_stdout(_stdout_buf):
        exec(compile(_student_code, "<student code>", "exec"), _ns)
    with contextlib.redirect_stdout(_stdout_buf):
        exec(compile(_test_code, "<test code>", "exec"), _ns)
    _result_passed = True
except SystemExit:
    _result_error = "SystemExit raised"
except Exception:
    _result_error = traceback.format_exc()
`;

    try {
      await pyodide.runPythonAsync(captureCode);
      passed = pyodide.globals.get("_result_passed") === true;
      stdout = String((pyodide.globals.get("_stdout_buf") as { getvalue: () => string }).getvalue?.() ?? "");
      const rawError = pyodide.globals.get("_result_error");
      error = (rawError !== null && rawError !== undefined) ? String(rawError) : null;
    } catch (e) {
      error = String(e);
      passed = false;
    }

    results.push({ name: tc.name, passed, stdout, error });
  }

  return results;
}


