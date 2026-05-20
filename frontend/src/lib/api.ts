import axios from "axios";
import type {
  InviteCodeOut,
  JobStatus,
  SnippetAdminOut,
  SnippetResponse,
  SnippetSummary,
  UserAdminOut,
  UserRead,
  UserStats,
} from "../types";

const api = axios.create({
  baseURL: "/api",
});

// Attach JWT token from localStorage to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Redirect to login on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

// ---- Auth ----
export const login = async (email: string, password: string): Promise<string> => {
  const form = new FormData();
  form.append("username", email);
  form.append("password", password);
  const { data } = await api.post<{ access_token: string }>("/auth/jwt/login", form);
  return data.access_token;
};

export const register = async (
  email: string,
  password: string,
  invite_code: string,
  display_name?: string
): Promise<UserRead> => {
  const { data } = await api.post<UserRead>("/auth/register", {
    email,
    password,
    invite_code,
    display_name,
  });
  return data;
};

export const getMe = async (): Promise<UserRead> => {
  const { data } = await api.get<UserRead>("/auth/me");
  return data;
};

// ---- Student: Stats & History ----
export const getMyStats = async (): Promise<UserStats> => {
  const { data } = await api.get<UserStats>("/me/stats");
  return data;
};

export const getMyHistory = async (solvedOnly = false): Promise<SnippetSummary[]> => {
  const { data } = await api.get<SnippetSummary[]>("/me/history", {
    params: { solved_only: solvedOnly },
  });
  return data;
};

// ---- Snippets ----
export const getNextSnippet = async (topic: string, difficulty: string): Promise<SnippetResponse> => {
  const { data } = await api.get<SnippetResponse>("/snippets/next", {
    params: { topic, difficulty },
  });
  return data;
};

// ---- Attempts ----
export const submitAttempt = async (
  snippet_id: string,
  tests: { name: string; passed: boolean; stdout: string; error: string | null }[]
): Promise<{ solved: boolean; attempt_count: number }> => {
  const { data } = await api.post("/attempts/submit", { snippet_id, tests });
  return data;
};

export const saveInProgressCode = async (snippet_id: string, code: string): Promise<void> => {
  await api.patch(`/attempts/${snippet_id}/code`, { code });
};

// ---- Admin: Invite Codes ----
export const listInviteCodes = async (): Promise<InviteCodeOut[]> => {
  const { data } = await api.get<InviteCodeOut[]>("/admin/invite-codes");
  return data;
};

export const generateInviteCodes = async (count: number): Promise<InviteCodeOut[]> => {
  const { data } = await api.post<InviteCodeOut[]>("/admin/invite-codes/generate", { count });
  return data;
};

export const revokeInviteCode = async (id: number): Promise<void> => {
  await api.delete(`/admin/invite-codes/${id}`);
};

// ---- Admin: Users ----
export const listUsers = async (): Promise<UserAdminOut[]> => {
  const { data } = await api.get<UserAdminOut[]>("/admin/users");
  return data;
};

export const updateUser = async (
  id: string,
  updates: { is_active?: boolean; is_admin?: boolean; display_name?: string }
): Promise<UserAdminOut> => {
  const { data } = await api.patch<UserAdminOut>(`/admin/users/${id}`, updates);
  return data;
};

export const deleteUser = async (id: string): Promise<void> => {
  await api.delete(`/admin/users/${id}`);
};

// ---- Admin: Snippets ----
export const listSnippets = async (topic?: string, difficulty?: string): Promise<SnippetAdminOut[]> => {
  const { data } = await api.get<SnippetAdminOut[]>("/admin/snippets", {
    params: { topic, difficulty },
  });
  return data;
};

export const updateSnippet = async (
  id: string,
  updates: Partial<Pick<SnippetAdminOut, "title" | "working_code" | "broken_code" | "test_cases" | "is_active">>
): Promise<SnippetAdminOut> => {
  const { data } = await api.patch<SnippetAdminOut>(`/admin/snippets/${id}`, updates);
  return data;
};

export const deleteSnippet = async (id: string): Promise<void> => {
  await api.delete(`/admin/snippets/${id}`);
};

export const createSnippet = async (
  payload: Pick<SnippetAdminOut, "topic" | "difficulty" | "title" | "working_code" | "broken_code" | "test_cases">
): Promise<SnippetAdminOut> => {
  const { data } = await api.post<SnippetAdminOut>("/admin/snippets", payload);
  return data;
};

// ---- Admin: Generation ----
export const triggerGeneration = async (topic: string, difficulty: string): Promise<JobStatus> => {
  const { data } = await api.post<JobStatus>("/admin/snippets/generate", { topic, difficulty });
  return data;
};

export const getJobStatus = async (job_id: string): Promise<JobStatus> => {
  const { data } = await api.get<JobStatus>(`/admin/snippets/jobs/${job_id}`);
  return data;
};

export default api;
