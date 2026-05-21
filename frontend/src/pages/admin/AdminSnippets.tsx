import { useEffect, useState } from "react";
import { deleteSnippet, listSnippets, updateSnippet } from "../../lib/api";
import type { SnippetAdminOut } from "../../types";
import { DIFFICULTIES, TOPICS } from "../../types";

export default function AdminSnippets() {
  const [snippets, setSnippets] = useState<SnippetAdminOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterTopic, setFilterTopic] = useState("");
  const [filterDiff, setFilterDiff] = useState("");
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const fetchSnippets = () => {
    setLoading(true);
    listSnippets(filterTopic || undefined, filterDiff || undefined)
      .then(setSnippets)
      .catch(() => setError("Failed to load snippets."))
      .finally(() => setLoading(false));
  };

  useEffect(fetchSnippets, [filterTopic, filterDiff]);

  const handleToggleActive = async (s: SnippetAdminOut) => {
    try {
      await updateSnippet(s.id, { is_active: !s.is_active });
      fetchSnippets();
    } catch {
      setError("Update failed.");
    }
  };

  const handleDelete = async (s: SnippetAdminOut) => {
    if (!confirm(`Delete snippet "${s.title}"? This cannot be undone.`)) return;
    try {
      await deleteSnippet(s.id);
      fetchSnippets();
    } catch {
      setError("Delete failed.");
    }
  };

  return (
    <div className="admin-section">
      <div className="admin-section-header">
        <h2>Snippets</h2>
        <div className="admin-filters">
          <select value={filterTopic} onChange={(e) => setFilterTopic(e.target.value)}>
            <option value="">All Topics</option>
            {TOPICS.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
          <select value={filterDiff} onChange={(e) => setFilterDiff(e.target.value)}>
            <option value="">All Difficulties</option>
            {DIFFICULTIES.map((d) => (
              <option key={d.value} value={d.value}>
                {d.label}
              </option>
            ))}
          </select>
          <span className="count-badge">{snippets.length} snippets</span>
        </div>
      </div>

      {error && <p className="form-error">{error}</p>}

      {loading ? (
        <div className="loading">Loading...</div>
      ) : (
        <table className="admin-table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Topic</th>
              <th>Difficulty</th>
              <th>Provider</th>
              <th>Active</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {snippets.map((s) => (
              <>
                <tr key={s.id} className={s.is_active ? "" : "row-inactive"}>
                  <td>
                    <button
                      className="btn-link"
                      onClick={() => setExpandedId(expandedId === s.id ? null : s.id)}
                    >
                      {s.title}
                    </button>
                  </td>
                  <td>{s.topic}</td>
                  <td className={`difficulty-${s.difficulty.toLowerCase()}`}>{s.difficulty}</td>
                  <td>{s.llm_provider}/{s.llm_model}</td>
                  <td>
                    <button
                      className={`toggle-btn ${s.is_active ? "active" : ""}`}
                      onClick={() => handleToggleActive(s)}
                    >
                      {s.is_active ? "Yes" : "No"}
                    </button>
                  </td>
                  <td>{new Date(s.created_at).toLocaleDateString()}</td>
                  <td>
                    <button
                      className="btn btn-danger-sm"
                      onClick={() => handleDelete(s)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
                {expandedId === s.id && (
                  <tr key={`${s.id}-detail`} className="snippet-detail-row">
                    <td colSpan={7}>
                      <div className="snippet-detail">
                        <div className="detail-section">
                          <strong>Working Code</strong>
                          <pre>{s.working_code}</pre>
                        </div>
                        <div className="detail-section">
                          <strong>Broken Code</strong>
                          <pre>{s.broken_code}</pre>
                        </div>
                        <div className="detail-section">
                          <strong>Test Cases</strong>
                          <pre>{JSON.stringify(s.test_cases, null, 2)}</pre>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
