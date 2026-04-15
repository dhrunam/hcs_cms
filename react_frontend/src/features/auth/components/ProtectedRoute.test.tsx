import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import { authStorage } from "@/shared/lib/authStorage";
import type { SessionUser } from "@/shared/types/auth";

import { ProtectedRoute } from "./ProtectedRoute";

const mockAdvocateUser: SessionUser = {
  id: 1,
  email: "advocate@example.com",
  fullName: "Advocate User",
  groups: ["ADVOCATE"],
  role: "advocate",
};

describe("ProtectedRoute", () => {
  beforeEach(() => {
    authStorage.clearSession();
  });

  it("redirects to login when user session is missing", () => {
    render(
      <MemoryRouter initialEntries={["/advocate"]}>
        <Routes>
          <Route path="/user/login" element={<div>Login page</div>} />
          <Route element={<ProtectedRoute />}>
            <Route path="/advocate" element={<div>Advocate dashboard</div>} />
          </Route>
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText("Login page")).toBeInTheDocument();
  });

  it("redirects to unauthorized when role is not allowed", () => {
    authStorage.setUser(mockAdvocateUser);

    render(
      <MemoryRouter initialEntries={["/judges"]}>
        <Routes>
          <Route path="/unauthorized" element={<div>Unauthorized</div>} />
          <Route element={<ProtectedRoute allowRoles={["judges"]} />}>
            <Route path="/judges" element={<div>Judges page</div>} />
          </Route>
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText("Unauthorized")).toBeInTheDocument();
  });
});
