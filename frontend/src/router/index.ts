import { createRouter, createWebHistory } from "vue-router";

import AccountPage from "../pages/AccountPage.vue";
import AdminPage from "../pages/AdminPage.vue";
import AnalysisWorkspacePage from "../pages/AnalysisWorkspacePage.vue";
import DashboardPage from "../pages/DashboardPage.vue";
import JobDescriptionsPage from "../pages/JobDescriptionsPage.vue";
import LoginPage from "../pages/LoginPage.vue";
import ProjectsPage from "../pages/ProjectsPage.vue";
import RegisterPage from "../pages/RegisterPage.vue";
import ResumeProfilePage from "../pages/ResumeProfilePage.vue";
import ResumeVersionsPage from "../pages/ResumeVersionsPage.vue";
import UsagePage from "../pages/UsagePage.vue";
import { authSession, clearSession, hasAccessToken, loadCurrentUser } from "../auth/session";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: DashboardPage },
    { path: "/resume", component: ResumeProfilePage },
    { path: "/projects", component: ProjectsPage },
    { path: "/jobs", component: JobDescriptionsPage },
    { path: "/analysis", component: AnalysisWorkspacePage },
    { path: "/versions", component: ResumeVersionsPage },
    { path: "/usage", component: UsagePage },
    { path: "/account", component: AccountPage },
    { path: "/admin", component: AdminPage },
    { path: "/login", component: LoginPage, meta: { public: true, guestOnly: true } },
    { path: "/register", component: RegisterPage, meta: { public: true, guestOnly: true } }
  ]
});

router.beforeEach(async (to) => {
  const isPublicRoute = to.meta.public === true;
  const isGuestOnlyRoute = to.meta.guestOnly === true;

  if (!authSession.initialized && hasAccessToken()) {
    try {
      await loadCurrentUser();
    } catch {
      clearSession();
    }
  } else if (!authSession.initialized) {
    clearSession();
  }

  if (isGuestOnlyRoute && authSession.user) {
    return "/";
  }

  if (!isPublicRoute && !authSession.user) {
    return {
      path: "/login",
      query: { redirect: to.fullPath }
    };
  }

  return true;
});
