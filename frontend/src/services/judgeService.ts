import { apiRequest } from "./apiClient";

export type Verdict = "AC" | "WA" | "TLE" | "MLE" | "CE" | "RE";

export interface TestCaseResult {
  test_id: number;
  execution_time_ms: number;
  verdict: Verdict;
  input: string;
  expected_output: string;
  actual_output: string;
  stderr?: string;
}

export interface SubmissionResponse {
  verdict: Verdict;
  message: string;
  execution_time_ms: number;
  tests_passed: number;
  total_tests: number;
  failed_test: TestCaseResult | null;
  tests: TestCaseResult[];
}

export interface SubmissionPayload {
  problem_id: string;
  source_code: string;
  language: "cpp" | "python";
}

export const judgeService = {
  async submit(payload: SubmissionPayload): Promise<SubmissionResponse> {
    return apiRequest<SubmissionResponse>("/api/judge/submit", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
};
