import { Navigate, Outlet } from "react-router-dom";

import { authStorage } from "../../../shared/lib/authStorage";
import type { UserRole } from "../../../shared/types/auth";

interface ProtectedRouteProps {
  allowRoles?: UserRole[];
}

export function ProtectedRoute({ allowRoles }: ProtectedRouteProps) {
  const user = authStorage.getUser();

  if (!user) {
    return <Navigate to="/user/login" replace />;
  }

  if (allowRoles && !allowRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <Outlet />;
}
