import { Link, Outlet, useNavigate } from "react-router-dom";

import { authStorage } from "../lib/authStorage";
import { normalizeApiError } from "../lib/apiError";
import { useToast } from "../lib/toast";
import type { UserRole } from "../types/auth";
import { logout } from "../../features/auth/api/authApi";
import { AdvocateNavbar } from "./AdvocateNavbar";
import { AdvocateSidebar } from "./AdvocateSidebar";
import "./advocate-shell.css";

type NavLink = {
  to: string;
  label: string;
};

const navByRole: Record<UserRole, NavLink[]> = {
  "party-in-person": [
    { to: "/party-in-person", label: "Overview" },
    { to: "/party-in-person/filings", label: "My Filings" },
  ],
  advocate: [
    { to: "/advocate/dashboard/home", label: "Overview" },
    { to: "/advocate/dashboard/efiling/filing", label: "Filings" },
  ],
  "scrutiny-officers": [
    { to: "/scrutiny-officers", label: "Overview" },
    { to: "/scrutiny-officers/queue", label: "Queue" },
  ],
  "listing-officers": [
    { to: "/listing-officers", label: "Overview" },
    { to: "/listing-officers/calendar", label: "Calendar" },
  ],
  judges: [
    { to: "/judges", label: "Overview" },
    { to: "/judges/board", label: "Board" },
  ],
  reader: [
    { to: "/reader", label: "Overview" },
    { to: "/reader/assignments", label: "Assignments" },
  ],
  steno: [
    { to: "/steno", label: "Overview" },
    { to: "/steno/transcripts", label: "Transcripts" },
  ],
};

export function AppShell() {
  const user = authStorage.getUser();
  const navigate = useNavigate();
  const { push } = useToast();
  const navLinks = user ? navByRole[user.role] : [];

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      const message = normalizeApiError(error, "Unable to notify server about logout.");
      push(message, "info");
    } finally {
      authStorage.clearSession();
      navigate("/user/login", { replace: true });
    }
  };

  if (user?.role === "advocate") {
    return (
      <div className="app-shell">
        <AdvocateNavbar />
        <div className="app-body app-body--advocate">
          <AdvocateSidebar />
          <section className="content">
            <Outlet />
          </section>
        </div>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <h1>HCS CMS</h1>
          <p>React platform</p>
        </div>
        <div className="topbar-actions">
          <span>{user?.fullName ?? user?.email ?? "User"}</span>
          <button onClick={() => void handleLogout()}>Logout</button>
        </div>
      </header>
      <div className="app-body">
        <aside className="sidebar">
          {navLinks.map((link) => (
            <Link key={link.to} to={link.to}>
              {link.label}
            </Link>
          ))}
        </aside>
        <section className="content">
          <Outlet />
        </section>
      </div>
    </div>
  );
}
