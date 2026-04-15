import { Link } from "react-router-dom";

export function UnauthorizedPage() {
  return (
    <main className="center-card">
      <h1>Access denied</h1>
      <p>You are signed in, but not allowed to view this section.</p>
      <Link to="/" className="primary-link">
        Go to home
      </Link>
    </main>
  );
}
