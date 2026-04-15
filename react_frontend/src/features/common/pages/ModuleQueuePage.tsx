import { useMemo } from "react";
import { useLocation } from "react-router-dom";

const queueTitleMap: Record<string, string> = {
  "/party-in-person/filings": "My Filings",
  "/advocate/filings": "Advocate Filings",
  "/scrutiny-officers/queue": "Scrutiny Queue",
  "/listing-officers/calendar": "Listing Calendar",
  "/judges/board": "Judge Board",
  "/reader/assignments": "Reader Assignments",
  "/steno/transcripts": "Transcript Queue",
};

export function ModuleQueuePage() {
  const location = useLocation();

  const title = useMemo(
    () => queueTitleMap[location.pathname] ?? "Module Work Queue",
    [location.pathname],
  );

  return (
    <div>
      <h2>{title}</h2>
      <p>This section is ready for the next phase of role-specific data workflows.</p>
    </div>
  );
}
