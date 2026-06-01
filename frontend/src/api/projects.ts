import { apiGet, apiPost } from "./client";

export interface ProjectCreate {
  name: string;
  project_type: string;
  role: string;
  tech_stack: string[];
  description: string;
  user_contribution: string;
  work_url?: string | null;
}

export interface ProjectRead {
  id: number;
  user_id: number;
  name: string;
  project_type: string;
  role: string;
  tech_stack: string[];
  description: string;
  user_contribution: string;
  work_url: string | null;
  created_at: string;
  updated_at: string;
}

export function createProject(payload: ProjectCreate): Promise<ProjectRead> {
  return apiPost<ProjectCreate, ProjectRead>("/projects", payload);
}

export function listProjects(): Promise<ProjectRead[]> {
  return apiGet<ProjectRead[]>("/projects");
}
