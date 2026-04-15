import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <main className="center-card">
      <h1>404</h1>
      <p>The page you requested does not exist.</p>
      <Link to="/" className="primary-link">
        Return home
      </Link>
    </main>
  );
}
