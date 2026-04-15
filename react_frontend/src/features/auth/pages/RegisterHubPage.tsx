import { Link } from "react-router-dom";

export function RegisterHubPage() {
  return (
    <main className="center-card">
      <h1>Create an account</h1>
      <p>Select your registration type.</p>
      <div className="action-row">
        <Link to="/user/register/party" className="primary-link">
          Register as Party in Person
        </Link>
        <Link to="/user/register/advocate" className="primary-link">
          Register as Advocate
        </Link>
      </div>
    </main>
  );
}
