import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";

import { normalizeApiError } from "../../../shared/lib/apiError";
import { useToast } from "../../../shared/lib/toast";
import { registerAdvocate } from "../api/authApi";
import { isValidEmail } from "../lib/validators";
import "../styles/auth-shell.css";
import "../styles/register-form.css";

type AdvocateFormState = {
  email: string;
  password: string;
  passwordConfirm: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  date_of_birth: string;
  address: string;
  gender: "M" | "F" | "O" | "U";
  bar_id: string;
  bar_id_file: File | null;
};

const initialFormState: AdvocateFormState = {
  email: "",
  password: "",
  passwordConfirm: "",
  first_name: "",
  last_name: "",
  phone_number: "",
  date_of_birth: "",
  address: "",
  gender: "U",
  bar_id: "",
  bar_id_file: null,
};

export function RegisterAdvocatePage() {
  const navigate = useNavigate();
  const { push } = useToast();
  const [form, setForm] = useState<AdvocateFormState>(initialFormState);
  const [showPassword, setShowPassword] = useState(false);
  const [showPassword2, setShowPassword2] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validate = (): string | null => {
    if (!form.email.trim()) return "Email is required.";
    if (!isValidEmail(form.email.trim())) return "Enter a valid email address.";
    if (!form.password) return "Password is required.";
    if (form.password.length < 8) return "Password must be at least 8 characters.";
    if (form.password !== form.passwordConfirm) return "Passwords do not match.";
    if (!form.first_name.trim() || !form.last_name.trim()) return "First and last name are required.";
    if (!form.phone_number.trim()) return "Phone number is required.";
    if (!form.date_of_birth) return "Date of birth is required.";
    if (!form.address.trim()) return "Address is required.";
    if (!form.bar_id.trim()) return "Bar ID is required.";
    if (!form.bar_id_file) return "Bar ID document is required.";
    return null;
  };

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const result = await registerAdvocate({
        email: form.email.trim(),
        password: form.password,
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        phone_number: form.phone_number.trim(),
        date_of_birth: form.date_of_birth,
        address: form.address.trim(),
        gender: form.gender,
        bar_id: form.bar_id.trim(),
        bar_id_file: form.bar_id_file,
      });

      if (result.email_verification_required) {
        if (result.verification_token) {
          push("Verify your email to continue.", "info");
          navigate(`/user/verify-email?token=${encodeURIComponent(result.verification_token)}`, {
            replace: true,
          });
          return;
        }

        push("Check your email for a verification link.", "info");
        navigate("/user/verify-email", { replace: true });
        return;
      }

      push("Registration successful. You can sign in now.", "success");
      navigate("/user/login?registered=1", { replace: true });
    } catch (error) {
      const message = normalizeApiError(error, "Registration failed. Please review your details and try again.");
      setError(message);
      push(message, "error");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-page-inner" style={{ paddingBottom: "2.5rem" }}>
        <div className="auth-card auth-card--wide">
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.75rem", flexWrap: "wrap" }}>
            <img className="auth-logo" src="/assets/icons/hcs_logo.jpeg" alt="" style={{ marginBottom: 0 }} />
            <div>
              <h1 className="auth-title" style={{ margin: 0 }}>Advocate</h1>
              <p className="auth-subtitle" style={{ margin: 0 }}>Register as counsel</p>
            </div>
          </div>

          <p className="auth-muted-text" style={{ marginBottom: "1rem" }}>
            <Link to="/user/register" className="auth-link">← Back to account type</Link>
          </p>

          {error ? (
            <div className="auth-alert" role="alert" aria-live="polite">
              {error}
            </div>
          ) : null}

          <form onSubmit={onSubmit} noValidate>
            <fieldset disabled={isSubmitting} style={{ border: "none", padding: 0, margin: 0 }}>
              <div className="auth-grid">
                <div>
                  <label className="auth-label" htmlFor="adv-email">Email</label>
                  <input id="adv-email" className="auth-input" type="email" value={form.email} onChange={(e) => setForm((prev) => ({ ...prev, email: e.target.value }))} required />
                </div>
                <div>
                  <label className="auth-label" htmlFor="adv-phone">Phone</label>
                  <input id="adv-phone" className="auth-input" value={form.phone_number} onChange={(e) => setForm((prev) => ({ ...prev, phone_number: e.target.value }))} required />
                </div>
                <div>
                  <label className="auth-label" htmlFor="adv-fn">First name</label>
                  <input id="adv-fn" className="auth-input" value={form.first_name} onChange={(e) => setForm((prev) => ({ ...prev, first_name: e.target.value }))} required />
                </div>
                <div>
                  <label className="auth-label" htmlFor="adv-ln">Last name</label>
                  <input id="adv-ln" className="auth-input" value={form.last_name} onChange={(e) => setForm((prev) => ({ ...prev, last_name: e.target.value }))} required />
                </div>
                <div>
                  <label className="auth-label" htmlFor="adv-dob">Date of birth</label>
                  <input id="adv-dob" className="auth-input" type="date" value={form.date_of_birth} onChange={(e) => setForm((prev) => ({ ...prev, date_of_birth: e.target.value }))} required />
                </div>
                <div>
                  <label className="auth-label" htmlFor="adv-gender">Gender</label>
                  <select id="adv-gender" className="auth-input" value={form.gender} onChange={(e) => setForm((prev) => ({ ...prev, gender: e.target.value as AdvocateFormState["gender"] }))}>
                    <option value="M">Male</option>
                    <option value="F">Female</option>
                    <option value="O">Other</option>
                    <option value="U">Prefer not to say</option>
                  </select>
                </div>
                <div className="auth-span-2">
                  <label className="auth-label" htmlFor="adv-address">Address</label>
                  <textarea id="adv-address" className="auth-input" value={form.address} onChange={(e) => setForm((prev) => ({ ...prev, address: e.target.value }))} rows={3} required />
                </div>
                <div>
                  <label className="auth-label" htmlFor="adv-bar-id">Bar ID</label>
                  <input id="adv-bar-id" className="auth-input" value={form.bar_id} onChange={(e) => setForm((prev) => ({ ...prev, bar_id: e.target.value }))} required />
                </div>
                <div>
                  <label className="auth-label" htmlFor="adv-bar-file">Bar ID document</label>
                  <input id="adv-bar-file" className="auth-input" type="file" accept=".pdf,.png,.jpg,.jpeg" onChange={(e) => setForm((prev) => ({ ...prev, bar_id_file: e.target.files?.[0] ?? null }))} required />
                </div>
                <div>
                  <label className="auth-label" htmlFor="adv-pass">Password</label>
                  <div className="password-wrap">
                    <input id="adv-pass" className="auth-input" type={showPassword ? "text" : "password"} value={form.password} onChange={(e) => setForm((prev) => ({ ...prev, password: e.target.value }))} required />
                    <button type="button" className="password-toggle" onClick={() => setShowPassword((prev) => !prev)} aria-label={showPassword ? "Hide password" : "Show password"}>
                      {showPassword ? "Hide" : "Show"}
                    </button>
                  </div>
                  <small className="auth-muted-text">At least 8 characters.</small>
                </div>
                <div>
                  <label className="auth-label" htmlFor="adv-pass2">Confirm password</label>
                  <div className="password-wrap">
                    <input id="adv-pass2" className="auth-input" type={showPassword2 ? "text" : "password"} value={form.passwordConfirm} onChange={(e) => setForm((prev) => ({ ...prev, passwordConfirm: e.target.value }))} required />
                    <button type="button" className="password-toggle" onClick={() => setShowPassword2((prev) => !prev)} aria-label={showPassword2 ? "Hide password" : "Show password"}>
                      {showPassword2 ? "Hide" : "Show"}
                    </button>
                  </div>
                </div>
              </div>

              <button type="submit" className="auth-btn-primary" style={{ marginTop: "1rem" }} disabled={isSubmitting} aria-busy={isSubmitting}>
                {isSubmitting ? <span className="auth-spinner" aria-hidden="true" /> : null}
                {isSubmitting ? "Submitting..." : "Create account"}
              </button>
            </fieldset>
          </form>

          <p className="auth-text-center auth-mt-3 auth-mb-2" style={{ fontSize: "0.85rem" }}>
            <Link to="/user/login" className="auth-link">Already registered? Sign in</Link>
          </p>
        </div>
      </div>

      <footer className="auth-footer">
        <Link to="/user/login">Sign in</Link>
        {" · "}
        <Link to="/user/register">Register</Link>
      </footer>
    </div>
  );
}
