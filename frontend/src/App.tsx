import { Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { RequireAdmin, RequireAuth } from "./components/RequireAuth";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Problem from "./pages/Problem";
import AdminLayout from "./pages/admin/AdminLayout";
import AdminCodes from "./pages/admin/AdminCodes";
import AdminUsers from "./pages/admin/AdminUsers";
import AdminSnippets from "./pages/admin/AdminSnippets";
import AdminGenerate from "./pages/admin/AdminGenerate";

function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Public */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Student */}
        <Route
          path="/dashboard"
          element={
            <RequireAuth>
              <Dashboard />
            </RequireAuth>
          }
        />
        <Route
          path="/problem"
          element={
            <RequireAuth>
              <Problem />
            </RequireAuth>
          }
        />

        {/* Admin */}
        <Route
          path="/admin"
          element={
            <RequireAdmin>
              <AdminLayout />
            </RequireAdmin>
          }
        >
          <Route index element={<Navigate to="codes" replace />} />
          <Route path="codes" element={<AdminCodes />} />
          <Route path="users" element={<AdminUsers />} />
          <Route path="snippets" element={<AdminSnippets />} />
          <Route path="generate" element={<AdminGenerate />} />
        </Route>

        {/* Default redirect */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AuthProvider>
  );
}

export default App
