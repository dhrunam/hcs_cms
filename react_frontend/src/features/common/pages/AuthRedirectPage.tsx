import { Navigate } from "react-router-dom";

import { authStorage } from "../../../shared/lib/authStorage";
import { getHomePathForRole } from "../../../shared/lib/roleHomePath";

export function AuthRedirectPage() {
  const user = authStorage.getUser();

  if (!user) {
    return <Navigate to="/user/login" replace />;
  }

  return <Navigate to={getHomePathForRole(user.role)} replace />;
}
