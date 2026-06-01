import { apiGet, apiPost } from "./client";

export type QuestionDifficulty = "easy" | "medium" | "hard";

export interface InterviewQuestionItem {
  question: string;
  reason: string;
  related_resume_section: string;
  difficulty: QuestionDifficulty;
  suggested_answer: string;
  answer_strategy: string;
  risk_reminder: string;
}

export interface InterviewQuestionCreate {
  resume_version_id: number;
}

export interface InterviewQuestionResultRead {
  id: number;
  user_id: number;
  resume_version_id: number;
  questions: InterviewQuestionItem[];
  summary: string;
  model_name: string;
  created_at: string;
}

export function createInterviewQuestionResult(
  payload: InterviewQuestionCreate
): Promise<InterviewQuestionResultRead> {
  return apiPost<InterviewQuestionCreate, InterviewQuestionResultRead>("/interview-question-results", payload);
}

export function listInterviewQuestionResults(resumeVersionId: number): Promise<InterviewQuestionResultRead[]> {
  return apiGet<InterviewQuestionResultRead[]>(`/interview-question-results?resume_version_id=${resumeVersionId}`);
}
