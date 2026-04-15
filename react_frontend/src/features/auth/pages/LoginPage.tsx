import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import { normalizeApiError } from "../../../shared/lib/apiError";
import { authStorage } from "../../../shared/lib/authStorage";
import { useToast } from "../../../shared/lib/toast";
import { fetchMe, login } from "../api/authApi";

export function LoginPage() {
  const navigate = useNavigate();
  const { push } = useToast();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const token = await login({ email, password });
      authStorage.setToken(token.access);
      authStorage.setRefreshToken(token.refresh);

      const user = await fetchMe();
      authStorage.setUser(user);
      navigate(`/${user.role}`, { replace: true });
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
    <main className="center-card">
      <h1>Sign in</h1>
      <p>Use your HCS CMS account to continue.</p>
      <form className="form-grid" onSubmit={onSubmit}>
        <label>
          Email
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        {error ? <p className="error">{error}</p> : null}
        <button type="submit" disabled={loading}>
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </main>
  );
}
