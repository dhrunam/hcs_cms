import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Link } from "react-router-dom";
import { useNavigate, useSearchParams } from "react-router-dom";

import { normalizeApiError } from "../../../shared/lib/apiError";
import { authStorage } from "../../../shared/lib/authStorage";
import { getHomePathForRole } from "../../../shared/lib/roleHomePath";
import { useToast } from "../../../shared/lib/toast";
import { fetchMe, login } from "../api/authApi";
import { isValidLoginIdentifier } from "../lib/validators";
import "../styles/auth-shell.css";
import "../styles/login.css";

export function LoginPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { push } = useToast();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const identifierInvalid = submitted && !isValidLoginIdentifier(identifier);

  useEffect(() => {
    if (searchParams.get("registered") === "1") {
      push("Account created. Sign in with your email or phone number.", "success");
    }

    const authError = searchParams.get("auth_error");
    const authErrorDescription = searchParams.get("auth_error_description");
    if (authError) {
      const message = authErrorDescription || `Sign-in failed: ${authError}`;
      setError(message);
      push(message, "error");
    }
  }, [searchParams, push]);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitted(true);
    if (!isValidLoginIdentifier(identifier)) {
      const message = "Enter a valid email address or phone number.";
      setError(message);
      return;
    }
    if (!password) {
      setError("Password is required.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const token = await login({ email: identifier.trim(), password });
      authStorage.setToken(token.access);
      authStorage.setRefreshToken(token.refresh);

      const user = await fetchMe();
      authStorage.setUser(user);
      navigate(getHomePathForRole(user.role), { replace: true });
    } catch (error) {
      const message = normalizeApiError(error, "Login failed. Check your credentials and try again.");
      setError(message);
      push(message, "error");
      authStorage.clearSession();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page login-page">
      <div className="auth-page-inner">
        <div className="auth-split">
          <aside className="auth-brand" aria-hidden="false">
            <h1>Sikkim High Court eFiling</h1>
            <p>Sign in to file cases, manage documents, and follow your matters in one place.</p>
          </aside>

          <div className="login-form-column">
            <div className="auth-card">
              <div className="auth-text-center">
                <img
                  className="auth-logo"
                  src="/assets/icons/hcs_logo.jpeg"
                  alt="High Court of Sikkim"
                />
                <h2 className="auth-title">Sign in</h2>
              </div>

              {error ? (
                <div className="auth-alert" role="alert" aria-live="polite">
                  {error}
                </div>
              ) : null}

              <form onSubmit={onSubmit} noValidate>
                <div className="form-grid">
                  <label className="auth-label" htmlFor="login-identifier">
                    Email or phone number
                  </label>
                  <input
                    id="login-identifier"
                    className={`auth-input${identifierInvalid ? " is-invalid" : ""}`}
                    type="text"
                    name="email"
                    value={identifier}
                    onChange={(e) => setIdentifier(e.target.value)}
                    autoComplete="username"
                    inputMode="text"
                    required
                    aria-invalid={identifierInvalid}
                    aria-describedby={identifierInvalid ? "login-id-err" : undefined}
                    placeholder="Email or phone number"
                  />
                  {identifierInvalid ? (
                    <small id="login-id-err" className="auth-inline-error">
                      Enter a valid email address or phone number (digits, spaces, +, -).
                    </small>
                  ) : null}

                  <label className="auth-label" htmlFor="login-password">
                    Password
                  </label>
                  <div className="password-wrap">
                    <input
                      id="login-password"
                      className="auth-input"
                      type={showPassword ? "text" : "password"}
                      name="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      autoComplete="current-password"
                      required
                      aria-describedby="login-pass-hint"
                    />
                    <button
                      type="button"
                      className="password-toggle"
                      onClick={() => setShowPassword((prev) => !prev)}
                      aria-pressed={showPassword}
                      aria-label={showPassword ? "Hide password" : "Show password"}
                    >
                      {showPassword ? "Hide" : "Show"}
                    </button>
                  </div>
                  <small id="login-pass-hint" className="auth-muted-text">
                    Never share your password.
                  </small>

                  <button
                    type="submit"
                    className="auth-btn-primary"
                    disabled={loading}
                    aria-busy={loading}
                  >
                    {loading ? <span className="auth-spinner" aria-hidden="true" /> : null}
                    {loading ? "Signing in..." : "Sign in"}
                  </button>
                </div>
              </form>

              <p className="auth-text-center auth-mt-3 auth-mb-2">
                <Link to="/user/register" className="auth-link">
                  Create an account
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
