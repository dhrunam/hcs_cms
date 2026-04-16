import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { authStorage } from "../../../shared/lib/authStorage";
import { http } from "../../../shared/lib/http";
import "../styles/advocate-dashboard-home.css";

type SummaryMetric = {
  label: string;
  value: string;
  tone: "primary" | "warning" | "success" | "danger";
};

type FilingRow = {
  status?: string | null;
};

type NotificationRow = {
  id?: number;
  message?: string;
  link_url?: string | null;
  created_at?: string | null;
};

type FilingListResponse = {
  results?: FilingRow[];
};

type NotificationResponse = {
  results?: NotificationRow[];
};

function extractResults<T>(payload: unknown): T[] {
  if (Array.isArray(payload)) {
    return payload as T[];
  }
  if (payload && typeof payload === "object" && Array.isArray((payload as { results?: unknown[] }).results)) {
    return (payload as { results: T[] }).results;
  }
  return [];
}

function statusLower(status: string | null | undefined): string {
  return (status ?? "").trim().toLowerCase();
}

function formatNotificationDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMinutes = Math.floor(diffMs / 60000);
  if (diffMinutes < 1) return "Just now";
  if (diffMinutes < 60) return `${diffMinutes}m ago`;
  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

function isInternalPath(url: string | null | undefined): boolean {
  return Boolean(url && url.startsWith("/"));
}

export function AdvocateDashboardPage() {
  const user = authStorage.getUser();
  const advocateName = (user?.fullName || "Advocate").trim();
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingNotifications, setIsLoadingNotifications] = useState(false);
  const [totalFilings, setTotalFilings] = useState(0);
  const [pendingFilings, setPendingFilings] = useState(0);
  const [approvedFilings, setApprovedFilings] = useState(0);
  const [objections, setObjections] = useState(0);
  const [notifications, setNotifications] = useState<NotificationRow[]>([]);

  useEffect(() => {
    const pageSize = 9999;
    let active = true;

    async function loadFilingCounts() {
      setIsLoading(true);
      try {
        const [draft, scrutiny, approved] = await Promise.all([
          http.get<FilingListResponse | FilingRow[]>(`/efiling/efilings/?is_draft=true&page_size=${pageSize}`),
          http.get<FilingListResponse | FilingRow[]>(
            `/efiling/efilings/?is_draft=false&status=NOT_ACCEPTED&page_size=${pageSize}`,
          ),
          http.get<FilingListResponse | FilingRow[]>(
            `/efiling/efilings/?is_draft=false&status=ACCEPTED&page_size=${pageSize}`,
          ),
        ]);

        if (!active) return;

        const rows = [
          ...extractResults<FilingRow>(draft.data),
          ...extractResults<FilingRow>(scrutiny.data),
          ...extractResults<FilingRow>(approved.data),
        ];

        setTotalFilings(rows.length);
        setPendingFilings(
          rows.filter((row) => {
            const status = statusLower(row.status);
            return (
              status === "under_scrutiny" ||
              status.includes("scrutiny") ||
              status.includes("pending") ||
              status === "draft" ||
              !status
            );
          }).length,
        );
        setApprovedFilings(rows.filter((row) => statusLower(row.status).includes("accept")).length);
        setObjections(
          rows.filter((row) => {
            const status = statusLower(row.status);
            return status.includes("reject") || status.includes("object");
          }).length,
        );
      } catch {
        if (!active) return;
        setTotalFilings(0);
        setPendingFilings(0);
        setApprovedFilings(0);
        setObjections(0);
      } finally {
        if (active) setIsLoading(false);
      }
    }

    async function loadNotifications() {
      setIsLoadingNotifications(true);
      try {
        const { data } = await http.get<NotificationResponse | NotificationRow[]>(
          "/efiling/notifications/?role=advocate",
        );
        if (!active) return;
        setNotifications(extractResults<NotificationRow>(data));
      } catch {
        if (!active) return;
        setNotifications([]);
      } finally {
        if (active) setIsLoadingNotifications(false);
      }
    }

    void loadFilingCounts();
    void loadNotifications();

    return () => {
      active = false;
    };
  }, []);

  const summaryMetrics: SummaryMetric[] = useMemo(
    () => [
      { label: "Total Filings", value: isLoading ? "-" : String(totalFilings), tone: "primary" },
      { label: "Pending", value: isLoading ? "-" : String(pendingFilings), tone: "warning" },
      { label: "Approved", value: isLoading ? "-" : String(approvedFilings), tone: "success" },
      { label: "Objections", value: isLoading ? "-" : String(objections), tone: "danger" },
    ],
    [isLoading, totalFilings, pendingFilings, approvedFilings, objections],
  );

  return (
    <section className="adv-home">
      <header className="adv-home-header">
        <div>
          <h2>Hi, {advocateName}</h2>
          <p>Manage your advocate filings easily</p>
        </div>
        <Link className="adv-btn-create" to="/advocate/dashboard/efiling/filing">
          <span aria-hidden="true">+</span>
          <span>New Filing</span>
        </Link>
      </header>

      <article className="adv-hero-card" aria-label="Live courtroom synchronizer">
        <div className="adv-hero-content">
          <div className="adv-hero-icon" aria-hidden="true">
            <span>CV</span>
          </div>
          <div>
            <h3>Live Courtroom Synchronizer</h3>
            <p>View your scheduled hearings and sync with the judge for real-time arguments.</p>
          </div>
        </div>
        <Link className="adv-btn-hearings" to="/advocate/dashboard/cause-list">
          View Today&apos;s Hearings
        </Link>
      </article>

      <div className="adv-summary-grid">
        {summaryMetrics.map((metric) => (
          <article key={metric.label} className="adv-stat-card">
            <span className={`adv-stat-dot ${metric.tone}`} aria-hidden="true" />
            <p>{metric.label}</p>
            <h4>{metric.value}</h4>
          </article>
        ))}
      </div>

      <section className="adv-notifications" aria-labelledby="adv-notifications-title">
        <header>
          <h3 id="adv-notifications-title">Notifications</h3>
        </header>
        {isLoadingNotifications ? <div className="adv-empty-state">Loading...</div> : null}
        {!isLoadingNotifications && notifications.length === 0 ? (
          <div className="adv-empty-state">No new notifications.</div>
        ) : null}
        {!isLoadingNotifications && notifications.length > 0 ? (
          <ul className="adv-notification-list">
            {notifications.map((item, index) => (
              <li key={item.id ?? `${item.message ?? "notification"}-${index}`}>
                {isInternalPath(item.link_url) ? (
                  <Link to={item.link_url ?? "#"} className="adv-notification-item">
                    <div>
                      <p>{item.message || "Notification"}</p>
                      <span>{formatNotificationDate(item.created_at)}</span>
                    </div>
                  </Link>
                ) : (
                  <div className="adv-notification-item">
                    <div>
                      <p>{item.message || "Notification"}</p>
                      <span>{formatNotificationDate(item.created_at)}</span>
                    </div>
                  </div>
                )}
              </li>
            ))}
          </ul>
        ) : null}
      </section>
    </section>
  );
}
