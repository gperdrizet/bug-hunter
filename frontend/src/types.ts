export interface UserRead {
  id: string;
  email: string;
  display_name: string | null;
  is_active: boolean;
  is_admin: boolean;
  is_superuser: boolean;
  is_verified: boolean;
}

export interface TopicStats {
  topic: string;
  solved: number;
  attempted: number;
}

export interface UserStats {
  total_solved: number;
  total_attempted: number;
  success_rate: number;
  by_topic: TopicStats[];
}

export interface SnippetSummary {
  snippet_id: string;
  title: string;
  topic: string;
  difficulty: string;
  solved_at: string | null;
  attempt_count: number;
}

export interface SnippetResponse {
  id: string;
  topic: string;
  difficulty: string;
  title: string;
  description: string | null;
  broken_code: string;
  test_cases: TestCase[];
  in_progress_code: string | null;
}

export interface TestCase {
  name: string;
  code: string;
}

export interface TestResult {
  name: string;
  passed: boolean;
  stdout: string;
  error: string | null;
}

export interface InviteCodeOut {
  id: number;
  code: string;
  is_active: boolean;
  created_at: string;
  used_at: string | null;
  used_by_id: string | null;
}

export interface UserAdminOut {
  id: string;
  email: string;
  display_name: string | null;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface SnippetAdminOut {
  id: string;
  topic: string;
  difficulty: string;
  title: string;
  description: string | null;
  working_code: string;
  broken_code: string;
  test_cases: TestCase[];
  llm_provider: string;
  llm_model: string;
  is_active: boolean;
  created_at: string;
}

export interface JobStatus {
  job_id: string;
  status: "pending" | "running" | "done" | "failed";
  snippet_id: string | null;
  error: string | null;
}

export const TOPICS = [
  { value: "data_types", label: "Data Types" },
  { value: "data_structures", label: "Data Structures" },
  { value: "operators", label: "Operators" },
  { value: "loops", label: "Loops" },
  { value: "functions", label: "Functions" },
  { value: "classes", label: "Classes" },
  { value: "error_handling", label: "Error Handling" },
  { value: "comprehensions", label: "Comprehensions" },
  { value: "decorators", label: "Decorators" },
  { value: "generators", label: "Generators" },
  { value: "file_io", label: "File I/O" },
  { value: "exceptions", label: "Exceptions" },
] as const;

export const DIFFICULTIES = [
  { value: "easy", label: "Easy" },
  { value: "medium", label: "Medium" },
  { value: "hard", label: "Hard" },
] as const;
