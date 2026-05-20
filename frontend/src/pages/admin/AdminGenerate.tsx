import { useEffect, useRef, useState } from "react";
import { getJobStatus, triggerGeneration } from "../../lib/api";
import type { JobStatus } from "../../types";
import { DIFFICULTIES, TOPICS } from "../../types";

const POLL_INTERVAL_MS = 2000;

export default function AdminGenerate() {
  const [topic, setTopic] = useState("functions");
  const [difficulty, setDifficulty] = useState("easy");
  const [jobs, setJobs] = useState<JobStatus[]>([]);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pollRefs = useRef<Record<string, ReturnType<typeof setInterval>>>({});

  const startPolling = (job_id: string) => {
    if (pollRefs.current[job_id]) return;
    pollRefs.current[job_id] = setInterval(async () => {
      try {
        const updated = await getJobStatus(job_id);
        setJobs((prev) =>
          prev.map((j) => (j.job_id === job_id ? updated : j))
        );
        if (updated.status === "done" || updated.status === "failed") {
          clearInterval(pollRefs.current[job_id]);
          delete pollRefs.current[job_id];
        }
      } catch {
        clearInterval(pollRefs.current[job_id]);
        delete pollRefs.current[job_id];
      }
    }, POLL_INTERVAL_MS);
  };

  // Clean up intervals on unmount
  useEffect(() => {
    return () => {
      Object.values(pollRefs.current).forEach(clearInterval);
    };
  }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    setError(null);
    try {
      const job = await triggerGeneration(topic, difficulty);
      setJobs((prev) => [job, ...prev]);
      startPolling(job.job_id);
    } catch {
      setError("Failed to start generation job.");
    } finally {
      setGenerating(false);
    }
  };

  const topicLabel = (v: string) =>
    TOPICS.find((t) => t.value === v)?.label ?? v;

  const diffLabel = (v: string) =>
    DIFFICULTIES.find((d) => d.value === v)?.label ?? v;

  return (
    <div className="admin-section">
      <div className="admin-section-header">
        <h2>Generate Snippets</h2>
      </div>

      <div className="generate-form">
        <div className="form-group">
          <label>Topic</label>
          <select value={topic} onChange={(e) => setTopic(e.target.value)}>
            {TOPICS.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label>Difficulty</label>
          <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
            {DIFFICULTIES.map((d) => (
              <option key={d.value} value={d.value}>
                {d.label}
              </option>
            ))}
          </select>
        </div>
        <button
          className="btn btn-primary"
          onClick={handleGenerate}
          disabled={generating}
        >
          {generating ? "Starting…" : "Generate Snippet"}
        </button>
      </div>

      {error && <p className="form-error">{error}</p>}

      <p className="generate-note">
        Each generation runs 3 LLM passes (working code → tests → broken code) and
        verifies each step server-side. This may take 30–60 seconds.
      </p>

      {jobs.length > 0 && (
        <div className="jobs-list">
          <h3>Recent Jobs</h3>
          {jobs.map((job) => (
            <div key={job.job_id} className={`job-item job-${job.status}`}>
              <div className="job-header">
                <span className="job-id">
                  {topicLabel(topic)} / {diffLabel(difficulty)}
                </span>
                <span className={`badge job-badge-${job.status}`}>
                  {job.status === "pending" && "Pending…"}
                  {job.status === "running" && "Running…"}
                  {job.status === "done" && "✓ Done"}
                  {job.status === "failed" && "✗ Failed"}
                </span>
              </div>
              {job.snippet_id && (
                <p className="job-detail">Snippet ID: {job.snippet_id}</p>
              )}
              {job.error && (
                <p className="job-error">{job.error}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
