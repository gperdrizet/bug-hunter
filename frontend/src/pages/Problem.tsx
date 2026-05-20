import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { getNextSnippet, saveInProgressCode, submitAttempt } from "../lib/api";
import { loadPyodide, runTests } from "../lib/pyodide";
import { useAuth } from "../context/AuthContext";
import CodeEditor from "../components/CodeEditor";
import TestResults from "../components/TestResults";
import SnippetSelector from "../components/SnippetSelector";
import type { SnippetResponse, TestResult } from "../types";

const AUTOSAVE_DELAY_MS = 1500;

export default function Problem() {
  const { user, logout } = useAuth();

  // Selector state
  const [topic, setTopic] = useState("functions");
  const [difficulty, setDifficulty] = useState("easy");

  // Snippet state
  const [snippet, setSnippet] = useState<SnippetResponse | null>(null);
  const [code, setCode] = useState("");
  const [snippetLoading, setSnippetLoading] = useState(false);
  const [snippetError, setSnippetError] = useState<string | null>(null);

  // Pyodide state
  const [pyodideReady, setPyodideReady] = useState(false);
  const [pyodideError, setPyodideError] = useState<string | null>(null);

  // Run state
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState<TestResult[]>([]);
  const [solved, setSolved] = useState(false);

  // Autosave
  const autosaveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Eager Pyodide load on mount
  useEffect(() => {
    loadPyodide()
      .then(() => setPyodideReady(true))
      .catch((e) => setPyodideError(String(e)));
  }, []);

  const fetchSnippet = useCallback(async () => {
    setSnippetError(null);
    setSnippetLoading(true);
    setResults([]);
    setSolved(false);
    try {
      const s = await getNextSnippet(topic, difficulty);
      setSnippet(s);
      setCode(s.in_progress_code ?? s.broken_code);
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      if (status === 404) {
        setSnippetError(
          "No more unseen snippets for this topic/difficulty. Ask your instructor to generate more!"
        );
      } else {
        setSnippetError("Failed to load snippet. Please try again.");
      }
      setSnippet(null);
    } finally {
      setSnippetLoading(false);
    }
  }, [topic, difficulty]);

  // Autosave in-progress code
  const handleCodeChange = (newCode: string) => {
    setCode(newCode);
    if (!snippet || solved) return;
    if (autosaveTimer.current) clearTimeout(autosaveTimer.current);
    autosaveTimer.current = setTimeout(() => {
      saveInProgressCode(snippet.id, newCode).catch(() => {/* silent */});
    }, AUTOSAVE_DELAY_MS);
  };

  const handleRun = async () => {
    if (!snippet || !pyodideReady || running) return;
    setRunning(true);
    setResults([]);
    try {
      const testResults = await runTests(code, snippet.test_cases);
      setResults(testResults);
      const allPassed = testResults.every((r) => r.passed);

      await submitAttempt(
        snippet.id,
        testResults.map((r) => ({
          name: r.name,
          passed: r.passed,
          stdout: r.stdout,
          error: r.error,
        }))
      );

      if (allPassed) {
        setSolved(true);
        if (autosaveTimer.current) clearTimeout(autosaveTimer.current);
      }
    } catch (e) {
      console.error("Run error:", e);
    } finally {
      setRunning(false);
    }
  };

  const handleGiveUp = () => {
    if (!snippet) return;
    setCode(snippet.broken_code);
    setResults([]);
  };

  return (
    <div className="problem-layout">
      {/* Top bar */}
      <header className="problem-header">
        <Link to="/dashboard" className="btn btn-ghost">
          ← Dashboard
        </Link>
        <SnippetSelector
          topic={topic}
          difficulty={difficulty}
          onTopicChange={setTopic}
          onDifficultyChange={setDifficulty}
          onFetch={fetchSnippet}
          loading={snippetLoading}
        />
        <div className="header-right">
          <span className="welcome-small">{user?.display_name ?? user?.email}</span>
          <button className="btn btn-ghost" onClick={logout}>
            Sign Out
          </button>
        </div>
      </header>

      {/* Main content */}
      {!snippet && !snippetLoading && !snippetError && (
        <div className="problem-empty">
          <p>Select a topic and difficulty, then click <strong>New Snippet</strong> to start.</p>
          <button className="btn btn-primary" onClick={fetchSnippet}>
            Get First Snippet
          </button>
        </div>
      )}

      {snippetError && (
        <div className="problem-empty">
          <p className="form-error">{snippetError}</p>
          <button className="btn btn-secondary" onClick={fetchSnippet}>
            Try Again
          </button>
        </div>
      )}

      {snippet && (
        <div className="problem-body">
          {/* Snippet info bar */}
          <div className="snippet-info">
            <span className="snippet-title">{snippet.title}</span>
            <span className={`badge difficulty-${snippet.difficulty.toLowerCase()}`}>
              {snippet.difficulty}
            </span>
            <span className="badge badge-topic">{snippet.topic}</span>
            {solved && <span className="badge badge-success">Solved!</span>}
          </div>

          {/* Editor + output split */}
          <div className="editor-output-split">
            <div className="editor-pane">
              <CodeEditor
                value={code}
                onChange={handleCodeChange}
                readOnly={solved}
              />
            </div>
            <div className="output-pane">
              {/* Controls */}
              <div className="run-controls">
                <button
                  className="btn btn-primary"
                  onClick={handleRun}
                  disabled={!pyodideReady || running || solved}
                  title={!pyodideReady ? "Loading Python runtime…" : ""}
                >
                  {running
                    ? "Running…"
                    : !pyodideReady
                    ? "Loading Python…"
                    : "▶  Run Tests"}
                </button>
                {!solved && (
                  <button
                    className="btn btn-ghost"
                    onClick={handleGiveUp}
                    disabled={running}
                    title="Show working solution"
                  >
                    Give Up
                  </button>
                )}
                {solved && (
                  <button className="btn btn-secondary" onClick={fetchSnippet}>
                    Next Snippet →
                  </button>
                )}
              </div>

              {pyodideError && (
                <p className="form-error">
                  Python runtime failed to load: {pyodideError}
                </p>
              )}

              <TestResults results={results} />

              {results.length === 0 && !running && (
                <div className="output-placeholder">
                  Fix the bug in the code, then click <strong>Run Tests</strong>.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
