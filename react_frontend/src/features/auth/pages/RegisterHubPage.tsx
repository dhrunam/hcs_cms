import { Link } from "react-router-dom";
import "../styles/auth-shell.css";
import "../styles/register-hub.css";

export function RegisterHubPage() {
  return (
    <div className="auth-page">
      <div className="auth-page-inner">
        <div className="register-hub-head auth-text-center auth-mb-2">
          <img className="auth-logo" src="/assets/icons/hcs_logo.jpeg" alt="High Court of Sikkim" />
          <h1 className="auth-title" style={{ color: "#f8fafc", marginTop: "0.5rem" }}>
            Create an account
          </h1>
          <p style={{ color: "rgba(248, 250, 252, 0.65)", marginBottom: 0 }}>
            Choose how you will appear before the court.
          </p>
        </div>

        <div className="hub-grid">
          <Link to="/user/register/advocate" className="hub-card">
            <span className="hub-card-icon" aria-hidden="true">
              ⚖
            </span>
            <h2 className="hub-card-title">Advocate</h2>
            <p className="hub-card-desc">
              Register as counsel. You will need your bar ID and supporting document upload.
            </p>
            <span className="hub-card-cta">
              Continue <span aria-hidden="true">→</span>
            </span>
          </Link>

          <Link to="/user/register/party" className="hub-card">
            <span className="hub-card-icon" aria-hidden="true">
              👤
            </span>
            <h2 className="hub-card-title">Party in person</h2>
            <p className="hub-card-desc">
              Register as an individual litigant. You will file and manage your own case materials.
            </p>
            <span className="hub-card-cta">
              Continue <span aria-hidden="true">→</span>
            </span>
          </Link>
        </div>

        <p className="auth-text-center auth-mt-3 auth-mb-2">
          <Link to="/user/login" className="auth-white-link">
            Already have an account? Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
