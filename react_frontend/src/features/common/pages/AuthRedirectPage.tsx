import { Navigate } from "react-router-dom";

import { authStorage } from "../../../shared/lib/authStorage";

export function AuthRedirectPage() {
  const user = authStorage.getUser();

  if (!user) {
    return <Navigate to="/user/login" replace />;
  }

  return <Navigate to={`/${user.role}`} replace />;
}
