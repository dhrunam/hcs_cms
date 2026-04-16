import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { normalizeApiError } from "../../../shared/lib/apiError";
import { useToast } from "../../../shared/lib/toast";
import { verifyEmail } from "../api/authApi";
import "../styles/auth-shell.css";
import "../styles/register-form.css";

export function VerifyEmailPage() {
  const { push } = useToast();
  const [searchParams] = useSearchParams();
  const initialToken = useMemo(() => searchParams.get("token") ?? "", [searchParams]);
  const [token, setToken] = useState(initialToken);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const doVerify = async (verificationToken: string) => {
    setMessage(null);
    setError(null);
    setIsLoading(true);

    try {
      await verifyEmail({ token: verificationToken });
      setMessage("Email verified successfully.");
      push("Email verified successfully.", "success");
    } catch (error) {
      const message = normalizeApiError(error, "Verification failed. Token may be invalid or expired.");
      setError(message);
      push(message, "error");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const queryToken = initialToken.trim();
    if (queryToken) {
      void doVerify(queryToken);
    }
  }, [initialToken]);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const verificationToken = token.trim();
    if (!verificationToken) {
      setError("Enter the verification token from your email.");
      return;
    }
    await doVerify(verificationToken);
  };

  return (
    <div className="auth-page">
      <div className="auth-page-inner">
        <div className="auth-card auth-card--wide">
          <img className="auth-logo" src="/assets/icons/hcs_logo.jpeg" alt="" style={{ display: "block", margin: "0 auto 0.75rem" }} />
          <h1 className="auth-title auth-text-center">Verify your email</h1>
          <p className="auth-subtitle auth-text-center">
            If you registered with email verification enabled, paste the token from your email below, or open the verification link you were sent.
          </p>

          {message ? (
            <div style={{ background: "#dcfce7", border: "1px solid #86efac", color: "#14532d", borderRadius: "10px", padding: "0.7rem 0.8rem" }} role="status" aria-live="polite">
              {message}
              <p style={{ marginBottom: 0, marginTop: "0.4rem" }}>
                <Link to="/user/login" className="auth-link">Continue to sign in</Link>
              </p>
            </div>
          ) : null}

          {error && !message ? (
            <div className="auth-alert" role="alert" aria-live="polite">
              {error}
            </div>
          ) : null}

          {!message ? (
            <form onSubmit={onSubmit} noValidate>
              <label className="auth-label" htmlFor="verify-token">Verification token</label>
              <input
                id="verify-token"
                className="auth-input"
                type="text"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                autoComplete="one-time-code"
                disabled={isLoading}
                aria-describedby="verify-hint"
              />
              <small id="verify-hint" className="auth-muted-text" style={{ display: "block", margin: "0.5rem 0 0.8rem" }}>
                In development, the token may also be shown once after registration.
              </small>
              <button type="submit" className="auth-btn-primary" aria-busy={isLoading} disabled={isLoading}>
                {isLoading ? <span className="auth-spinner" aria-hidden="true" /> : null}
                {isLoading ? "Verifying..." : "Verify email"}
              </button>
            </form>
          ) : null}

          <p className="auth-text-center auth-mt-3 auth-mb-2" style={{ fontSize: "0.85rem" }}>
            <Link to="/user/login" className="auth-link">Back to sign in</Link>
          </p>
        </div>
      </div>

      <footer className="auth-footer">
        <Link to="/user/register">Register</Link>
      </footer>
    </div>
  );
}
