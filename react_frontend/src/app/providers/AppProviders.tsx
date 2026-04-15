import { RouterProvider } from "react-router-dom";

import { ToastProvider } from "../../shared/lib/toast";
import { router } from "../routes/router";

export function AppProviders() {
  return (
    <ToastProvider>
      <RouterProvider router={router} />
    </ToastProvider>
  );
}
