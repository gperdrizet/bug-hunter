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

    const captureCode = `
import sys
import io
import contextlib

_stdout_buf = io.StringIO()
_result_passed = False
_result_error = None

try:
    with contextlib.redirect_stdout(_stdout_buf):
${indent(studentCode, 8)}
        
    with contextlib.redirect_stdout(_stdout_buf):
${indent(tc.code, 8)}
    _result_passed = True
except AssertionError as e:
    _result_error = f"AssertionError: {e}"
except Exception as e:
    _result_error = f"{type(e).__name__}: {e}"
except SystemExit:
    _result_error = "SystemExit raised"
`;

    try {
      await pyodide.runPythonAsync(captureCode);
      passed = pyodide.globals.get("_result_passed") as boolean;
      stdout = (pyodide.globals.get("_stdout_buf") as { getvalue: () => string }).getvalue?.() ?? "";
      error = pyodide.globals.get("_result_error") as string | null;
    } catch (e) {
      error = String(e);
      passed = false;
    }

    results.push({ name: tc.name, passed, stdout, error });
  }

  return results;
}

function indent(code: string, spaces: number): string {
  const pad = " ".repeat(spaces);
  return code
    .split("\n")
    .map((line) => pad + line)
    .join("\n");
}
