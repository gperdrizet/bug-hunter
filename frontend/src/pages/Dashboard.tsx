import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getMyHistory, getMyStats } from "../lib/api";
import { useAuth } from "../context/AuthContext";
import type { SnippetSummary, UserStats } from "../types";
import { DIFFICULTIES, TOPICS } from "../types";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [history, setHistory] = useState<SnippetSummary[]>([]);
  const [solvedOnly, setSolvedOnly] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getMyStats(), getMyHistory(solvedOnly)])
      .then(([s, h]) => {
        setStats(s);
        setHistory(h);
      })
      .finally(() => setLoading(false));
  }, [solvedOnly]);

  const topicLabel = (value: string) =>
    TOPICS.find((t) => t.value === value.toLowerCase())?.label ?? value;

  const difficultyLabel = (value: string) =>
    DIFFICULTIES.find((d) => d.value === value.toLowerCase())?.label ?? value;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-left">
          <h1><img src="/bug-hunter.svg" className="nav-logo" alt="" />Bug Hunter</h1>
          <span className="welcome">
            Welcome, {user?.display_name ?? user?.email}
          </span>
        </div>
        <nav className="header-nav">
          <Link to="/problem" className="btn btn-primary">
            Practice
          </Link>
          {user?.is_admin && (
            <Link to="/admin" className="btn btn-secondary">
              Admin
            </Link>
          )}
          <button className="btn btn-ghost" onClick={logout}>
            Sign Out
          </button>
        </nav>
      </header>

      {loading ? (
        <div className="loading">Loading stats...</div>
      ) : (
        <>
          <section className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{stats?.total_solved ?? 0}</div>
              <div className="stat-label">Bugs Fixed</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats?.total_attempted ?? 0}</div>
              <div className="stat-label">Snippets Tried</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">
                {stats ? Math.round(stats.success_rate) : 0}%
              </div>
              <div className="stat-label">Success Rate</div>
            </div>
          </section>

          {stats && stats.by_topic.length > 0 && (
            <section className="topic-stats">
              <h2>Progress by Topic</h2>
              <div className="topic-grid">
                {stats.by_topic.map((t) => (
                  <div key={t.topic} className="topic-card">
                    <div className="topic-name">{topicLabel(t.topic)}</div>
                    <div className="topic-progress">
                      {t.solved}/{t.attempted} solved
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          <section className="history">
            <div className="history-header">
              <h2>History</h2>
              <label className="filter-toggle">
                <input
                  type="checkbox"
                  checked={solvedOnly}
                  onChange={(e) => setSolvedOnly(e.target.checked)}
                />
                Solved only
              </label>
            </div>
            {history.length === 0 ? (
              <p className="empty-state">
                No snippets yet.{" "}
                <Link to="/problem">Start practicing!</Link>
              </p>
            ) : (
              <table className="history-table">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Topic</th>
                    <th>Difficulty</th>
                    <th>Submissions</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((h) => (
                    <tr key={h.snippet_id}>
                      <td>
                        {h.solved_at ? (
                          h.title
                        ) : (
                          <Link to={`/problem?resume=${h.snippet_id}`}>{h.title}</Link>
                        )}
                      </td>
                      <td>{topicLabel(h.topic)}</td>
                      <td className={`difficulty-${h.difficulty.toLowerCase()}`}>
                        {difficultyLabel(h.difficulty)}
                      </td>
                      <td>{h.attempt_count}</td>
                      <td>
                        {h.solved_at ? (
                          <span className="badge badge-success">Solved</span>
                        ) : (
                          <span className="badge badge-pending">In Progress</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>
        </>
      )}
    </div>
  );
}
