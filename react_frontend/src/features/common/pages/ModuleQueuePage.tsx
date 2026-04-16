import { useMemo } from "react";
import { useLocation } from "react-router-dom";

const queueTitleMap: Record<string, string> = {
  "/party-in-person/filings": "My Filings",
  "/advocate/filings": "Advocate Filings",
  "/advocate/dashboard/cause-list": "Cause List",
  "/advocate/dashboard/efiling/filing": "Case Filing",
  "/advocate/dashboard/efiling/new-filing": "New Filing",
  "/advocate/dashboard/efiling/draft-filings": "Draft Filings",
  "/advocate/dashboard/efiling/document-filing/list": "Document Filing",
  "/advocate/dashboard/efiling/document-filing/create": "Create Document Filing",
  "/advocate/dashboard/efiling/ia-filing": "IA Filing",
  "/advocate/dashboard/efiling/pending-scrutiny": "Pending Scrutiny",
  "/advocate/dashboard/efiling/approved-cases": "Approved Cases",
  "/scrutiny-officers/queue": "Scrutiny Queue",
  "/listing-officers/calendar": "Listing Calendar",
  "/judges/board": "Judge Board",
  "/reader/assignments": "Reader Assignments",
  "/steno/transcripts": "Transcript Queue",
};

function getTitleByPath(pathname: string): string {
  if (queueTitleMap[pathname]) {
    return queueTitleMap[pathname];
  }

  if (pathname.startsWith("/advocate/dashboard/courtview/")) {
    return "Courtview";
  }

  return "Module Work Queue";
}

export function ModuleQueuePage() {
  const location = useLocation();

  const title = useMemo(() => getTitleByPath(location.pathname), [location.pathname]);

  return (
    <div>
      <h2>{title}</h2>
      <p>This section is ready for the next phase of role-specific data workflows.</p>
    </div>
  );
}
