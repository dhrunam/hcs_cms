import { lazy, Suspense } from "react";
import type { ReactNode } from "react";
import { createBrowserRouter, Navigate } from "react-router-dom";

import { ProtectedRoute } from "../../features/auth/components/ProtectedRoute";

import { AppShell } from "../../shared/layouts/AppShell";

const LoginPage = lazy(() => import("../../features/auth/pages/LoginPage").then((module) => ({ default: module.LoginPage })));
const RegisterAdvocatePage = lazy(() =>
  import("../../features/auth/pages/RegisterAdvocatePage").then((module) => ({
    default: module.RegisterAdvocatePage,
  })),
);
const RegisterHubPage = lazy(() =>
  import("../../features/auth/pages/RegisterHubPage").then((module) => ({
    default: module.RegisterHubPage,
  })),
);
const RegisterPartyPage = lazy(() =>
  import("../../features/auth/pages/RegisterPartyPage").then((module) => ({
    default: module.RegisterPartyPage,
  })),
);
const VerifyEmailPage = lazy(() =>
  import("../../features/auth/pages/VerifyEmailPage").then((module) => ({
    default: module.VerifyEmailPage,
  })),
);
const AdvocateDashboardPage = lazy(() =>
  import("../../features/advocate/pages/AdvocateDashboardPage").then((module) => ({
    default: module.AdvocateDashboardPage,
  })),
);
const AuthRedirectPage = lazy(() =>
  import("../../features/common/pages/AuthRedirectPage").then((module) => ({
    default: module.AuthRedirectPage,
  })),
);
const ModuleQueuePage = lazy(() =>
  import("../../features/common/pages/ModuleQueuePage").then((module) => ({
    default: module.ModuleQueuePage,
  })),
);
const NotFoundPage = lazy(() =>
  import("../../features/common/pages/NotFoundPage").then((module) => ({
    default: module.NotFoundPage,
  })),
);
const UnauthorizedPage = lazy(() =>
  import("../../features/common/pages/UnauthorizedPage").then((module) => ({
    default: module.UnauthorizedPage,
  })),
);
const JudgeDashboardPage = lazy(() =>
  import("../../features/judges/pages/JudgeDashboardPage").then((module) => ({
    default: module.JudgeDashboardPage,
  })),
);
const ListingOfficerDashboardPage = lazy(() =>
  import("../../features/listing-officers/pages/ListingOfficerDashboardPage").then((module) => ({
    default: module.ListingOfficerDashboardPage,
  })),
);
const PartyDashboardPage = lazy(() =>
  import("../../features/party/pages/PartyDashboardPage").then((module) => ({
    default: module.PartyDashboardPage,
  })),
);
const ReaderDashboardPage = lazy(() =>
  import("../../features/reader/pages/ReaderDashboardPage").then((module) => ({
    default: module.ReaderDashboardPage,
  })),
);
const ScrutinyOfficerDashboardPage = lazy(() =>
  import("../../features/scrutiny-officers/pages/ScrutinyOfficerDashboardPage").then((module) => ({
    default: module.ScrutinyOfficerDashboardPage,
  })),
);
const StenoDashboardPage = lazy(() =>
  import("../../features/steno/pages/StenoDashboardPage").then((module) => ({
    default: module.StenoDashboardPage,
  })),
);

function withSuspense(element: ReactNode) {
  return <Suspense fallback={<main className="center-card">Loading module...</main>}>{element}</Suspense>;
}

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Navigate to="/auth/redirect" replace />,
  },
  {
    path: "/auth/redirect",
    element: withSuspense(<AuthRedirectPage />),
  },
  {
    path: "/user/login",
    element: withSuspense(<LoginPage />),
  },
  {
    path: "/user/register",
    element: withSuspense(<RegisterHubPage />),
  },
  {
    path: "/user/register/party",
    element: withSuspense(<RegisterPartyPage />),
  },
  {
    path: "/user/register/advocate",
    element: withSuspense(<RegisterAdvocatePage />),
  },
  {
    path: "/user/verify-email",
    element: withSuspense(<VerifyEmailPage />),
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppShell />,
        children: [
          {
            element: <ProtectedRoute allowRoles={["party-in-person"]} />,
            children: [
              {
                path: "/party-in-person",
                children: [
                  {
                    index: true,
                    element: withSuspense(<PartyDashboardPage />),
                  },
                  {
                    path: "filings",
                    element: withSuspense(<ModuleQueuePage />),
                  },
                ],
              },
            ],
          },
          {
            element: <ProtectedRoute allowRoles={["advocate"]} />,
            children: [
              {
                path: "/advocate",
                children: [
                  {
                    index: true,
                    element: withSuspense(<AdvocateDashboardPage />),
                  },
                  {
                    path: "filings",
                    element: withSuspense(<ModuleQueuePage />),
                  },
                ],
              },
            ],
          },
          {
            element: <ProtectedRoute allowRoles={["scrutiny-officers"]} />,
            children: [
              {
                path: "/scrutiny-officers",
                children: [
                  {
                    index: true,
                    element: withSuspense(<ScrutinyOfficerDashboardPage />),
                  },
                  {
                    path: "queue",
                    element: withSuspense(<ModuleQueuePage />),
                  },
                ],
              },
            ],
          },
          {
            element: <ProtectedRoute allowRoles={["listing-officers"]} />,
            children: [
              {
                path: "/listing-officers",
                children: [
                  {
                    index: true,
                    element: withSuspense(<ListingOfficerDashboardPage />),
                  },
                  {
                    path: "calendar",
                    element: withSuspense(<ModuleQueuePage />),
                  },
                ],
              },
            ],
          },
          {
            element: <ProtectedRoute allowRoles={["judges"]} />,
            children: [
              {
                path: "/judges",
                children: [
                  {
                    index: true,
                    element: withSuspense(<JudgeDashboardPage />),
                  },
                  {
                    path: "board",
                    element: withSuspense(<ModuleQueuePage />),
                  },
                ],
              },
            ],
          },
          {
            element: <ProtectedRoute allowRoles={["reader"]} />,
            children: [
              {
                path: "/reader",
                children: [
                  {
                    index: true,
                    element: withSuspense(<ReaderDashboardPage />),
                  },
                  {
                    path: "assignments",
                    element: withSuspense(<ModuleQueuePage />),
                  },
                ],
              },
            ],
          },
          {
            element: <ProtectedRoute allowRoles={["steno"]} />,
            children: [
              {
                path: "/steno",
                children: [
                  {
                    index: true,
                    element: withSuspense(<StenoDashboardPage />),
                  },
                  {
                    path: "transcripts",
                    element: withSuspense(<ModuleQueuePage />),
                  },
                ],
              },
            ],
          },
        ],
      },
    ],
  },
  {
    path: "/unauthorized",
    element: withSuspense(<UnauthorizedPage />),
  },
  {
    path: "*",
    element: withSuspense(<NotFoundPage />),
  },
]);
