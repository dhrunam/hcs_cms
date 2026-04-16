import { useState } from "react";
import "../styles/filing.css";
import NewFilingTab from "./filing/NewFilingTab";
import ExistingCaseFilingTab from "./filing/ExistingCaseFilingTab";
import IaFilingTab from "./filing/IaFilingTab";

type FilingTab = "new" | "existing" | "ia" | "vakalatnama" | "caveat";

const TABS: { id: FilingTab; label: string; icon: string }[] = [
  { id: "new", label: "New Filing", icon: "fa-solid fa-plus" },
  { id: "existing", label: "Existing Case Filing", icon: "fa-solid fa-folder-open" },
  { id: "ia", label: "IA Filing", icon: "fa-solid fa-file-lines" },
  { id: "vakalatnama", label: "Vakalatnama Filing", icon: "fa-solid fa-file-signature" },
  { id: "caveat", label: "Caveat Filing", icon: "fa-solid fa-shield-halved" },
];

export default function FilingPage() {
  const [activeTab, setActiveTab] = useState<FilingTab>("new");

  return (
    <div className="filing-page">
      {/* Hero */}
      <div className="filing-hero">
        <p className="filing-eyebrow">E-Filing</p>
        <h1 className="filing-title">Case Filing</h1>
        <p className="filing-subtitle">
          Select the filing type below to get started with your submission.
        </p>

        <div className="filing-switcher">
          <div className="filing-toggle">
            {TABS.map((tab) => (
              <label
                key={tab.id}
                className={`filing-radio${activeTab === tab.id ? " active" : ""}`}
                onClick={() => setActiveTab(tab.id)}
              >
                <input
                  type="radio"
                  name="filing-tab"
                  value={tab.id}
                  checked={activeTab === tab.id}
                  onChange={() => setActiveTab(tab.id)}
                />
                <i className={tab.icon} />
                {tab.label}
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* Panel */}
      <div className="filing-panel">
        {activeTab === "new" && <NewFilingTab />}
        {activeTab === "existing" && <ExistingCaseFilingTab />}
        {activeTab === "ia" && <IaFilingTab />}
        {activeTab === "vakalatnama" && (
          <div className="filing-tab-placeholder">
            <h3 className="filing-tab-placeholder-title">Vakalatnama Filing</h3>
            <p className="filing-tab-placeholder-text">
              Vakalatnama filing functionality is coming soon. Please check back later.
            </p>
          </div>
        )}
        {activeTab === "caveat" && (
          <div className="filing-tab-placeholder">
            <h3 className="filing-tab-placeholder-title">Caveat Filing</h3>
            <p className="filing-tab-placeholder-text">
              Caveat filing functionality is coming soon. Please check back later.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
