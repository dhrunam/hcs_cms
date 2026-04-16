import { useEffect, useRef, useState } from "react";
import type { MouseEvent } from "react";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";

import { authStorage } from "../lib/authStorage";
import { normalizeApiError } from "../lib/apiError";
import { useToast } from "../lib/toast";
import { logout } from "../../features/auth/api/authApi";

export function AdvocateNavbar() {
  const navigate = useNavigate();
  const { push } = useToast();
  const [currentTime, setCurrentTime] = useState("");
  const [currentDate, setCurrentDate] = useState("");
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function updateClock() {
      const now = new Date();
      setCurrentTime(
        now.toLocaleTimeString("en-IN", {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
          hour12: true,
        }),
      );
      setCurrentDate(
        now.toLocaleDateString("en-IN", {
          weekday: "short",
          day: "numeric",
          month: "short",
        }),
      );
    }
    updateClock();
    const id = setInterval(updateClock, 1000);
    return () => clearInterval(id);
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    function onPointerDown(e: PointerEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("pointerdown", onPointerDown);
    return () => document.removeEventListener("pointerdown", onPointerDown);
  }, []);

  const handleLogout = async (e: MouseEvent) => {
    e.preventDefault();
    try {
      await logout();
    } catch (error) {
      push(normalizeApiError(error, "Unable to notify server about logout."), "info");
    } finally {
      authStorage.clearSession();
      navigate("/user/login", { replace: true });
    }
  };

  return (
    <nav className="adv-navbar" role="banner">
      <div className="adv-navbar-brand">
        <Link to="/advocate/dashboard/home" className="adv-brand-link">
          <img src="/assets/icons/advocate-logo.png" height="40" alt="" aria-hidden="true" />
          <span className="adv-brand-text">Advocate</span>
        </Link>
      </div>

      <div className="adv-navbar-right">
        <div className="adv-clock" aria-live="off" aria-atomic="true">
          <div className="adv-clock-date">{currentDate}</div>
          <div className="adv-clock-time">{currentTime}</div>
        </div>

        <Link to="/advocate/dashboard/cause-list" className="adv-courtroom-btn">
          <i className="fa-solid fa-gavel" aria-hidden="true" />
          <span>Courtroom Mode</span>
        </Link>

        <span className="adv-bell" aria-label="Notifications">
          <i className="fa-solid fa-bell" aria-hidden="true" />
        </span>

        <div className="adv-user-dropdown" ref={dropdownRef}>
          <button
            className="adv-user-toggle"
            onClick={() => setDropdownOpen((p) => !p)}
            aria-haspopup="menu"
            aria-expanded={dropdownOpen}
            aria-label="User menu"
          >
            <i className="fa-solid fa-circle-user" aria-hidden="true" />
          </button>

          {dropdownOpen && (
            <ul className="adv-dropdown-menu" role="menu">
              <li role="none">
                <button
                  className="adv-dropdown-item adv-dropdown-danger"
                  role="menuitem"
                  onClick={(e) => void handleLogout(e)}
                >
                  <i className="fa-solid fa-right-from-bracket" aria-hidden="true" />
                  Logout
                </button>
              </li>
            </ul>
          )}
        </div>
      </div>
    </nav>
  );
}
