import { useState } from "react";
import { NavLink } from "react-router-dom";

type SubItem = { to: string; label: string };
type LinkItem = { kind: "link"; to: string; label: string; icon: string; className?: string };
type GroupItem = { kind: "group"; label: string; icon: string; id: string; items: SubItem[] };
type MenuItem = LinkItem | GroupItem;

const MENU: MenuItem[] = [
  {
    kind: "link",
    to: "/advocate/dashboard/home",
    label: "Dashboard",
    icon: "fa-solid fa-chart-line",
  },
  {
    kind: "group",
    label: "Filing",
    icon: "fa-solid fa-file",
    id: "filing",
    items: [
      { to: "/advocate/dashboard/efiling/filing", label: "Filing" },
      { to: "/advocate/dashboard/efiling/draft-filings", label: "Drafts" },
    ],
  },
  {
    kind: "group",
    label: "My Filings",
    icon: "fa-solid fa-suitcase",
    id: "my-filings",
    items: [
      { to: "/advocate/dashboard/efiling/pending-scrutiny", label: "Pending Filings" },
      { to: "/advocate/dashboard/efiling/approved-cases", label: "Approved Filings" },
    ],
  },
  {
    kind: "link",
    to: "/advocate/dashboard/cause-list",
    label: "Courtroom Mode",
    icon: "fa-solid fa-gavel",
    className: "adv-sidebar-courtroom",
  },
];

export function AdvocateSidebar() {
  const [openGroup, setOpenGroup] = useState<string | null>(null);
  const toggle = (id: string) => setOpenGroup((prev) => (prev === id ? null : id));

  return (
    <aside className="adv-sidebar" aria-label="Advocate navigation">
      <ul className="adv-sidebar-nav" role="list">
        {MENU.map((item) => {
          if (item.kind === "link") {
            return (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  end={item.to === "/advocate/dashboard/home"}
                  className={({ isActive }) =>
                    `adv-nav-link${item.className ? ` ${item.className}` : ""}${isActive ? " active" : ""}`
                  }
                >
                  <i className={item.icon} aria-hidden="true" />
                  {item.label}
                </NavLink>
              </li>
            );
          }

          const isOpen = openGroup === item.id;
          return (
            <li key={item.id}>
              <button
                className="adv-nav-link adv-nav-group-toggle"
                onClick={() => toggle(item.id)}
                aria-expanded={isOpen}
                aria-controls={`submenu-${item.id}`}
              >
                <span className="adv-nav-group-label">
                  <i className={item.icon} aria-hidden="true" />
                  {item.label}
                </span>
                <i
                  className={`fa-solid fa-chevron-down adv-chevron${isOpen ? " open" : ""}`}
                  aria-hidden="true"
                />
              </button>

              <ul
                id={`submenu-${item.id}`}
                className="adv-sub-nav"
                hidden={!isOpen}
                role="list"
              >
                {item.items.map((sub) => (
                  <li key={sub.to}>
                    <NavLink
                      to={sub.to}
                      className={({ isActive }) => `adv-sub-link${isActive ? " active" : ""}`}
                    >
                      {sub.label}
                    </NavLink>
                  </li>
                ))}
              </ul>
            </li>
          );
        })}
      </ul>
    </aside>
  );
}
