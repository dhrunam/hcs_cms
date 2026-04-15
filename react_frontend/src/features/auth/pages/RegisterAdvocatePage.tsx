import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";

import { normalizeApiError } from "../../../shared/lib/apiError";
import { useToast } from "../../../shared/lib/toast";
import { registerAdvocate } from "../api/authApi";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

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
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validate = (): string | null => {
    if (!form.email.trim()) return "Email is required.";
    if (!EMAIL_RE.test(form.email.trim())) return "Enter a valid email address.";
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
      await registerAdvocate({
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
    <main className="center-card">
      <h1>Advocate Registration</h1>
      <form className="form-grid" onSubmit={onSubmit}>
        <label>
          Email
          <input
            type="email"
            value={form.email}
            onChange={(e) => setForm((prev) => ({ ...prev, email: e.target.value }))}
            required
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={form.password}
            onChange={(e) => setForm((prev) => ({ ...prev, password: e.target.value }))}
            required
          />
        </label>
        <label>
          Confirm password
          <input
            type="password"
            value={form.passwordConfirm}
            onChange={(e) => setForm((prev) => ({ ...prev, passwordConfirm: e.target.value }))}
            required
          />
        </label>
        <label>
          First name
          <input
            value={form.first_name}
            onChange={(e) => setForm((prev) => ({ ...prev, first_name: e.target.value }))}
            required
          />
        </label>
        <label>
          Last name
          <input
            value={form.last_name}
            onChange={(e) => setForm((prev) => ({ ...prev, last_name: e.target.value }))}
            required
          />
        </label>
        <label>
          Phone number
          <input
            value={form.phone_number}
            onChange={(e) => setForm((prev) => ({ ...prev, phone_number: e.target.value }))}
            required
          />
        </label>
        <label>
          Date of birth
          <input
            type="date"
            value={form.date_of_birth}
            onChange={(e) => setForm((prev) => ({ ...prev, date_of_birth: e.target.value }))}
            required
          />
        </label>
        <label>
          Address
          <textarea
            value={form.address}
            onChange={(e) => setForm((prev) => ({ ...prev, address: e.target.value }))}
            rows={3}
            required
          />
        </label>
        <label>
          Gender
          <select
            value={form.gender}
            onChange={(e) =>
              setForm((prev) => ({ ...prev, gender: e.target.value as AdvocateFormState["gender"] }))
            }
          >
            <option value="U">Prefer not to say</option>
            <option value="M">Male</option>
            <option value="F">Female</option>
            <option value="O">Other</option>
          </select>
        </label>
        <label>
          Bar ID
          <input
            value={form.bar_id}
            onChange={(e) => setForm((prev) => ({ ...prev, bar_id: e.target.value }))}
            required
          />
        </label>
        <label>
          Bar ID document
          <input
            type="file"
            accept=".pdf,.png,.jpg,.jpeg"
            onChange={(e) =>
              setForm((prev) => ({ ...prev, bar_id_file: e.target.files?.[0] ?? null }))
            }
            required
          />
        </label>
        {error ? <p className="error">{error}</p> : null}
        <div className="action-row">
          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Submitting..." : "Register"}
          </button>
          <Link to="/user/login">Back to login</Link>
        </div>
      </form>
    </main>
  );
}
