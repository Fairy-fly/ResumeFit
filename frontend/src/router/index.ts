import { createRouter, createWebHistory } from "vue-router";

import AnalysisWorkspacePage from "../pages/AnalysisWorkspacePage.vue";
import DashboardPage from "../pages/DashboardPage.vue";
import JobDescriptionsPage from "../pages/JobDescriptionsPage.vue";
import ProjectsPage from "../pages/ProjectsPage.vue";
import ResumeProfilePage from "../pages/ResumeProfilePage.vue";
import ResumeVersionsPage from "../pages/ResumeVersionsPage.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: DashboardPage },
    { path: "/resume", component: ResumeProfilePage },
    { path: "/projects", component: ProjectsPage },
    { path: "/jobs", component: JobDescriptionsPage },
    { path: "/analysis", component: AnalysisWorkspacePage },
    { path: "/versions", component: ResumeVersionsPage }
  ]
});
