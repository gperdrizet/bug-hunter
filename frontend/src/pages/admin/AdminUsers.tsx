import { useEffect, useState } from "react";
import { deleteUser, listUsers, updateUser } from "../../lib/api";
import { useAuth } from "../../context/AuthContext";
import type { UserAdminOut } from "../../types";

export default function AdminUsers() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState<UserAdminOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchUsers = () => {
    setLoading(true);
    listUsers()
      .then(setUsers)
      .catch(() => setError("Failed to load users."))
      .finally(() => setLoading(false));
  };

  useEffect(fetchUsers, []);

  const handleToggle = async (u: UserAdminOut, field: "is_active" | "is_admin") => {
    try {
      await updateUser(u.id, { [field]: !u[field] });
      fetchUsers();
    } catch {
      setError("Update failed.");
    }
  };

  const handleDelete = async (u: UserAdminOut) => {
    if (!confirm(`Delete user ${u.email}? This cannot be undone.`)) return;
    try {
      await deleteUser(u.id);
      fetchUsers();
    } catch {
      setError("Delete failed.");
    }
  };

  return (
    <div className="admin-section">
      <div className="admin-section-header">
        <h2>Users</h2>
        <span className="count-badge">{users.length} total</span>
      </div>

      {error && <p className="form-error">{error}</p>}

      {loading ? (
        <div className="loading">Loading…</div>
      ) : (
        <table className="admin-table">
          <thead>
            <tr>
              <th>Email</th>
              <th>Display Name</th>
              <th>Joined</th>
              <th>Active</th>
              <th>Admin</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className={u.is_active ? "" : "row-inactive"}>
                <td>{u.email}</td>
                <td>{u.display_name ?? "—"}</td>
                <td>{new Date(u.created_at).toLocaleDateString()}</td>
                <td>
                  <button
                    className={`toggle-btn ${u.is_active ? "active" : ""}`}
                    onClick={() => handleToggle(u, "is_active")}
                    disabled={u.id === currentUser?.id}
                  >
                    {u.is_active ? "Yes" : "No"}
                  </button>
                </td>
                <td>
                  <button
                    className={`toggle-btn ${u.is_admin ? "active" : ""}`}
                    onClick={() => handleToggle(u, "is_admin")}
                    disabled={u.id === currentUser?.id}
                  >
                    {u.is_admin ? "Yes" : "No"}
                  </button>
                </td>
                <td>
                  <button
                    className="btn btn-danger-sm"
                    onClick={() => handleDelete(u)}
                    disabled={u.id === currentUser?.id}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
