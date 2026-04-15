import { useMemo, useState } from "react";
import type { FormEvent } from "react";
import { useSearchParams } from "react-router-dom";

import { normalizeApiError } from "../../../shared/lib/apiError";
import { useToast } from "../../../shared/lib/toast";
import { verifyEmail } from "../api/authApi";

export function VerifyEmailPage() {
  const { push } = useToast();
  const [searchParams] = useSearchParams();
  const initialToken = useMemo(() => searchParams.get("token") ?? "", [searchParams]);
  const [token, setToken] = useState(initialToken);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setMessage(null);
    setError(null);

    try {
      await verifyEmail({ token });
      setMessage("Email verified successfully. You can now sign in.");
      push("Email verified successfully.", "success");
    } catch (error) {
      const message = normalizeApiError(error, "Verification failed. Token may be invalid or expired.");
      setError(message);
      push(message, "error");
    }
  };

  return (
    <main className="center-card">
      <h1>Verify Email</h1>
      <form className="form-grid" onSubmit={onSubmit}>
        <label>
          Verification token
          <input value={token} onChange={(e) => setToken(e.target.value)} required />
        </label>
        {message ? <p>{message}</p> : null}
        {error ? <p className="error">{error}</p> : null}
        <button type="submit">Verify</button>
      </form>
    </main>
  );
}
