import { Link, NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function AdminLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="admin-layout">
      <aside className="admin-sidebar">
        <div className="admin-logo">
          <Link to="/dashboard">Bug Hunter</Link>
        </div>
        <nav className="admin-nav">
          <NavLink
            to="/admin/codes"
            className={({ isActive }) => (isActive ? "admin-nav-link active" : "admin-nav-link")}
          >
            Invite Codes
          </NavLink>
          <NavLink
            to="/admin/users"
            className={({ isActive }) => (isActive ? "admin-nav-link active" : "admin-nav-link")}
          >
            Users
          </NavLink>
          <NavLink
            to="/admin/snippets"
            className={({ isActive }) => (isActive ? "admin-nav-link active" : "admin-nav-link")}
          >
            Snippets
          </NavLink>
          <NavLink
            to="/admin/generate"
            className={({ isActive }) => (isActive ? "admin-nav-link active" : "admin-nav-link")}
          >
            Generate
          </NavLink>
        </nav>
        <div className="admin-footer">
          <span>{user?.display_name ?? user?.email}</span>
          <button className="btn btn-ghost" onClick={logout}>
            Sign Out
          </button>
        </div>
      </aside>
      <main className="admin-content">
        <Outlet />
      </main>
    </div>
  );
}
