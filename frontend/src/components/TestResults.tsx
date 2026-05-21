import type { TestResult } from "../types";

interface TestResultsProps {
  results: TestResult[];
}

export default function TestResults({ results }: TestResultsProps) {
  if (results.length === 0) return null;

  const allPassed = results.every((r) => r.passed);

  return (
    <div className="test-results">
      <div className={`overall-status ${allPassed ? "status-pass" : "status-fail"}`}>
        {allPassed ? "All tests passed!" : "Some tests failed"}
      </div>
      <div className="test-list">
        {results.map((r, i) => (
          <div key={i} className={`test-item ${r.passed ? "test-pass" : "test-fail"}`}>
            <div className="test-name">
              <span className="test-icon">{r.passed ? "PASS" : "FAIL"}</span>
              {r.name}
            </div>
            {r.stdout && (
              <pre className="test-output">{r.stdout}</pre>
            )}
            {r.error && (
              <pre className="test-error">{r.error}</pre>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
