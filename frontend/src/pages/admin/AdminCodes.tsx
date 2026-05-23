import { useEffect, useState } from "react";
import { generateInviteCodes, listInviteCodes, revokeInviteCode } from "../../lib/api";
import type { InviteCodeOut } from "../../types";

export default function AdminCodes() {
  const [codes, setCodes] = useState<InviteCodeOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [count, setCount] = useState(5);
  const [error, setError] = useState<string | null>(null);

  const fetchCodes = () => {
    setLoading(true);
    listInviteCodes()
      .then(setCodes)
      .catch(() => setError("Failed to load codes."))
      .finally(() => setLoading(false));
  };

  useEffect(fetchCodes, []);

  const handleGenerate = async () => {
    setGenerating(true);
    setError(null);
    try {
      await generateInviteCodes(count);
      fetchCodes();
    } catch {
      setError("Failed to generate codes.");
    } finally {
      setGenerating(false);
    }
  };

  const handleRevoke = async (id: number) => {
    if (!confirm("Revoke this invite code?")) return;
    try {
      await revokeInviteCode(id);
      fetchCodes();
    } catch {
      setError("Failed to revoke code.");
    }
  };

  const copyCode = (code: string) => {
    navigator.clipboard.writeText(code);
  };

  return (
    <div className="admin-section">
      <div className="admin-section-header">
        <h2>Invite Codes</h2>
        <div className="admin-actions">
          <input
            type="number"
            min={1}
            max={100}
            value={count}
            onChange={(e) => setCount(Number(e.target.value))}
            className="count-input"
          />
          <button className="btn btn-primary" onClick={handleGenerate} disabled={generating}>
            {generating ? "Generating…" : `Generate ${count} Code${count !== 1 ? "s" : ""}`}
          </button>
        </div>
      </div>

      {error && <p className="form-error">{error}</p>}

      {loading ? (
        <div className="loading">Loading…</div>
      ) : (
        <table className="admin-table">
          <thead>
            <tr>
              <th>Code</th>
              <th>Active</th>
              <th>Created</th>
              <th>Used At</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {codes.map((c) => (
              <tr key={c.id} className={c.is_active ? "" : "row-inactive"}>
                <td>
                  <code>{c.code}</code>
                  <button className="btn-icon" onClick={() => copyCode(c.code)} title="Copy">
                    📋
                  </button>
                </td>
                <td>{c.is_active ? "Yes" : "No"}</td>
                <td>{new Date(c.created_at).toLocaleDateString()}</td>
                <td>{c.used_at ? new Date(c.used_at).toLocaleDateString() : "-"}</td>
                <td>
                  {c.is_active && (
                    <button
                      className="btn btn-danger-sm"
                      onClick={() => handleRevoke(c.id)}
                    >
                      Revoke
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
