import { Routes } from "@angular/router";

export const EfilingRoutes: Routes = [
  {
    path: "filing",
    loadComponent: () => import("./filing/filing").then((c) => c.Filing),
  },
  {
    path: "new-filing",
    loadComponent: () =>
      import("./new-filing/new-filing").then((c) => c.NewFiling),
  },
  
  {
    path: "draft-filings",
    loadChildren: () =>
      import("./draft-filings/draft-filing.routing").then(
        (r) => r.DraftFilingRoutes,
      ),
  },
  {
    path: "approved-cases",
    loadComponent: () =>
      import("./approved-cases/approved-cases").then((c) => c.ApprovedCases),
  },
  {
    path: "pending-scrutiny",
    loadChildren: () =>
      import("./cases-scrutiny/cases-scrutiny-routing-module").then(
        (c) => c.routes,
      ),
  },
  {
    path: "document-filing",
    loadChildren: () =>
      import("./document-filing/document-filing.routing").then(
        (r) => r.DocumentFilingRoutes,
      ),
  },
  {
    path: "ia-filing",
    loadChildren: () =>
      import("./ia-filing/ia-filing.routing").then((r) => r.IaFilingRoutes),
  },
];
