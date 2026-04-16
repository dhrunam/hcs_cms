import { useState, useEffect, useMemo } from "react";
import { http } from "../../../../shared/lib/http";
import "../../styles/new-filing.css";

type LitigantType = "PETITIONER" | "RESPONDENT" | "APPELLANT";

const LITIGANT_TYPE_OPTIONS: { value: LitigantType; label: string }[] = [
  { value: "PETITIONER", label: "Petitioner" },
  { value: "RESPONDENT", label: "Respondent" },
  { value: "APPELLANT", label: "Appellant" },
];

interface FilingWithLitigants {
  filing: any;
  litigants: any[];
}

function getLitigantLabel(item: FilingWithLitigants): string {
  const petitioners = item.litigants.filter((l: any) => l.is_petitioner).map((l: any) => l.name || "-").join(", ");
  const respondents = item.litigants.filter((l: any) => !l.is_petitioner).map((l: any) => l.name || "-").join(", ");
  if (petitioners && respondents) return `${petitioners} vs ${respondents}`;
  if (petitioners) return petitioners;
  return item.filing.petitioner_name || "—";
}

export default function ExistingCaseFilingTab() {
  const [filingsWithLitigants, setFilingsWithLitigants] = useState<FilingWithLitigants[]>([]);
  const [isLoadingFilings, setIsLoadingFilings] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [selectedFiling, setSelectedFiling] = useState<any>(null);
  const [litigantType, setLitigantType] = useState<LitigantType>("PETITIONER");

  /* ── IA selection ── */
  const [iaList, setIaList] = useState<any[]>([]);
  const [iaSearchQuery, setIaSearchQuery] = useState("");
  const [iaDropdownOpen, setIaDropdownOpen] = useState(false);
  const [selectedIa, setSelectedIa] = useState<any>(null);

  /* ── Document upload ── */
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [documentType, setDocumentType] = useState("Document");
  const [existingDocs, setExistingDocs] = useState<any[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  /* ── Load filings + litigants ── */

  useEffect(() => {
    setIsLoadingFilings(true);
    http.get("/api/v1/efiling/efilings/")
      .then(async (res) => {
        const filings: any[] = res.data?.results ?? res.data ?? [];
        const valid = filings.filter((f: any) => f?.id && f?.e_filing_number);
        // Load litigants for each filing
        const pairs = await Promise.all(
          valid.map(async (filing) => {
            try {
              const lr = await http.get(`/api/v1/efiling/efiling-litigants/?efiling_id=${filing.id}`);
              const litigants: any[] = lr.data?.results ?? lr.data ?? [];
              return { filing, litigants };
            } catch {
              return { filing, litigants: [] };
            }
          })
        );
        setFilingsWithLitigants(pairs);
        setIsLoadingFilings(false);
      })
      .catch(() => {
        setFilingsWithLitigants([]);
        setIsLoadingFilings(false);
      });
  }, []);

  /* ── Filtered list ── */

  const filteredFilings = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return filingsWithLitigants;
    return filingsWithLitigants.filter((item) => {
      const efNo = (item.filing.e_filing_number || "").toLowerCase();
      const ct = (item.filing.case_type?.type_name || "").toLowerCase();
      const label = getLitigantLabel(item).toLowerCase();
      return efNo.includes(q) || ct.includes(q) || label.includes(q);
    });
  }, [filingsWithLitigants, searchQuery]);

  const filteredIaList = useMemo(() => {
    const q = iaSearchQuery.trim().toLowerCase();
    if (!q) return iaList;
    return iaList.filter((ia) => {
      return (ia.ia_number || "").toLowerCase().includes(q) || (ia.ia_text || "").toLowerCase().includes(q);
    });
  }, [iaList, iaSearchQuery]);

  /* ── Select filing ── */

  const selectFiling = async (item: FilingWithLitigants) => {
    setSelectedFiling(item.filing);
    setIsDropdownOpen(false);
    setSelectedIa(null);
    setExistingDocs([]);
    // Load existing docs
    try {
      const dr = await http.get(`/api/v1/efiling/efiling-documents/?efiling_id=${item.filing.id}`);
      setExistingDocs(dr.data?.results ?? dr.data ?? []);
    } catch {}
    // Load IA list
    try {
      const ir = await http.get(`/api/v1/efiling/ia-filing/ia-filings/?efiling_id=${item.filing.id}`);
      setIaList(ir.data?.results ?? ir.data ?? []);
    } catch {
      setIaList([]);
    }
  };

  const getSelectedLabel = () => {
    if (!selectedFiling) return "";
    const item = filingsWithLitigants.find((x) => x.filing.id === selectedFiling.id);
    return `${selectedFiling.e_filing_number} (${selectedFiling.case_type?.type_name || "N/A"})${item ? " — " + getLitigantLabel(item) : ""}`;
  };

  /* ── Upload document ── */

  const handleUpload = async () => {
    if (!selectedFile || !selectedFiling) return;
    setIsUploading(true);
    const fd = new FormData();
    fd.append("efiling_id", String(selectedFiling.id));
    fd.append("document_type", documentType);
    fd.append("litigant_type", litigantType);
    fd.append("final_document", selectedFile);
    if (selectedIa) fd.append("ia_id", String(selectedIa.id));
    try {
      await http.post("/api/v1/efiling/efiling-documents/", fd);
      // Refresh docs
      const dr = await http.get(`/api/v1/efiling/efiling-documents/?efiling_id=${selectedFiling.id}`);
      setExistingDocs(dr.data?.results ?? dr.data ?? []);
      setSelectedFile(null);
      setUploadSuccess(true);
      setTimeout(() => setUploadSuccess(false), 3000);
    } catch (e: any) {
      alert(e?.response?.data?.detail || "Upload failed.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteDoc = async (id: number) => {
    if (!window.confirm("Remove this document?")) return;
    try {
      await http.delete(`/api/v1/efiling/efiling-documents/${id}/`);
      setExistingDocs((prev) => prev.filter((d) => d.id !== id));
    } catch {
      alert("Failed to delete document.");
    }
  };

  return (
    <div className="document-filing-create">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h5 className="mb-0">File Documents</h5>
      </div>

      {/* Step 1: Select Case */}
      <div className="card border-0 shadow-sm mb-4" style={{ borderRadius: 12 }}>
        <div className="card-header bg-dark text-white fw-semibold" style={{ borderRadius: "12px 12px 0 0" }}>
          <i className="fa-solid fa-folder-open me-2" />
          Select Case
        </div>
        <div className="card-body">
          <label className="form-label">Search &amp; select an e-filing to add documents</label>

          {/* Searchable dropdown */}
          <div className={`searchable-select${isDropdownOpen ? " open" : ""}`}>
            {isDropdownOpen && (
              <div className="searchable-select-backdrop" onClick={() => setIsDropdownOpen(false)} />
            )}
            <button
              type="button"
              className="form-select-selector"
              disabled={isLoadingFilings}
              onClick={() => setIsDropdownOpen((o) => !o)}
            >
              {selectedFiling ? (
                <span style={{ color: "#111827" }}>{getSelectedLabel()}</span>
              ) : (
                <span className="text-muted">-- Search by E-Filing No, Case Type, Petitioner or Respondent --</span>
              )}
              <i className={`fa-solid fa-chevron-down ms-2${isDropdownOpen ? " rotate-180" : ""}`} style={{ transition: "transform 0.2s", transform: isDropdownOpen ? "rotate(180deg)" : "none" }} />
            </button>

            {isDropdownOpen && (
              <div className="searchable-select-dropdown">
                <div className="searchable-select-search">
                  <i className="fa-solid fa-search text-muted" />
                  <input
                    type="text"
                    placeholder="Type to search..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onClick={(e) => e.stopPropagation()}
                    autoFocus
                  />
                </div>
                <div className="searchable-select-list">
                  {filteredFilings.map((item) => (
                    <button
                      key={item.filing.id}
                      type="button"
                      className={`searchable-select-option${selectedFiling?.id === item.filing.id ? " selected" : ""}`}
                      onClick={() => selectFiling(item)}
                    >
                      <div className="d-flex justify-content-between align-items-start gap-2">
                        <div>
                          <span className="fw-semibold text-dark">{item.filing.e_filing_number}</span>
                          <span className="text-muted small ms-1">({item.filing.case_type?.type_name || "N/A"})</span>
                        </div>
                      </div>
                      <div className="petitioner-vs-respondent mt-1">{getLitigantLabel(item)}</div>
                    </button>
                  ))}
                  {filteredFilings.length === 0 && (
                    <div className="text-muted small p-3 text-center">No matching e-filing found.</div>
                  )}
                </div>
              </div>
            )}
          </div>

          {isLoadingFilings && <div className="text-muted small mt-1">Loading filings...</div>}

          {/* Filing As */}
          {selectedFiling && (
            <div className="mt-4">
              <label className="form-label" htmlFor="existing-case-litigant-type">Filing As</label>
              <select
                id="existing-case-litigant-type"
                className="form-select"
                value={litigantType}
                onChange={(e) => setLitigantType(e.target.value as LitigantType)}
                style={{ maxWidth: 240 }}
              >
                {LITIGANT_TYPE_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
          )}

          {/* IA selection */}
          {selectedFiling && (
            <div className="mt-4">
              <label className="form-label">
                Search &amp; select IA{" "}
                {selectedIa && (
                  <span className="text-muted fw-normal">
                    (<a
                      href="#"
                      className="text-decoration-none"
                      onClick={(e) => { e.preventDefault(); setSelectedIa(null); }}
                    >Clear</a>)
                  </span>
                )}
              </label>
              <div className={`searchable-select${iaDropdownOpen ? " open" : ""}`}>
                {iaDropdownOpen && (
                  <div className="searchable-select-backdrop" onClick={() => setIaDropdownOpen(false)} />
                )}
                <button
                  type="button"
                  className="form-select-selector"
                  onClick={() => setIaDropdownOpen((o) => !o)}
                >
                  {selectedIa ? (
                    <span className="text-dark">{selectedIa.ia_number || `IA #${selectedIa.id}`}</span>
                  ) : (
                    <span className="text-muted">-- Search by IA number, status or relief sought --</span>
                  )}
                  <i className="fa-solid fa-chevron-down ms-2" style={{ transform: iaDropdownOpen ? "rotate(180deg)" : "none", transition: "transform 0.2s" }} />
                </button>
                {iaDropdownOpen && (
                  <div className="searchable-select-dropdown">
                    <div className="searchable-select-search">
                      <i className="fa-solid fa-search text-muted" />
                      <input
                        type="text"
                        placeholder="Type to search..."
                        value={iaSearchQuery}
                        onChange={(e) => setIaSearchQuery(e.target.value)}
                        onClick={(e) => e.stopPropagation()}
                        autoFocus
                      />
                    </div>
                    <div className="searchable-select-list">
                      {filteredIaList.map((ia) => (
                        <button
                          key={ia.id}
                          type="button"
                          className={`searchable-select-option${selectedIa?.id === ia.id ? " selected" : ""}`}
                          onClick={() => { setSelectedIa(ia); setIaDropdownOpen(false); }}
                        >
                          <span className="fw-semibold text-dark">{ia.ia_number || "-"}</span>
                          {ia.ia_text && (
                            <div className="text-muted small mt-1">{ia.ia_text.slice(0, 80)}{ia.ia_text.length > 80 ? "..." : ""}</div>
                          )}
                        </button>
                      ))}
                      {filteredIaList.length === 0 && (
                        <div className="text-muted small p-3 text-center">No IAs found for this e-filing.</div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Step 2: Upload Documents */}
      {selectedFiling && (
        <div className="card border-0 shadow-sm mb-4" style={{ borderRadius: 12 }}>
          <div className="card-header bg-dark text-white fw-semibold" style={{ borderRadius: "12px 12px 0 0" }}>
            <i className="fa-solid fa-upload me-2" />
            Upload Documents
          </div>
          <div className="card-body">
            {/* Existing docs */}
            {existingDocs.length > 0 && (
              <div className="mb-4">
                <div className="section-title mb-2">Uploaded Documents</div>
                <div className="list-group list-group-flush">
                  {existingDocs.map((doc, i) => (
                    <div key={doc.id} className="list-group-item doc-slot-row">
                      <div className="d-flex justify-content-between align-items-center">
                        <span className="fw-semibold">{i + 1}. {doc.document_type}</span>
                        <button className="btn btn-sm btn-outline-danger" onClick={() => handleDeleteDoc(doc.id)}>
                          <i className="fa fa-trash" /> delete
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Upload form */}
            <div className="row g-3" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <div>
                <label className="form-label">Document Type</label>
                <input
                  className="form-control"
                  value={documentType}
                  onChange={(e) => setDocumentType(e.target.value)}
                  style={{ borderRadius: 12, padding: "5px 15px", border: "1px solid #d1d5db" }}
                />
              </div>
              <div>
                <label className="form-label">Select PDF</label>
                <div
                  className="drop-zone"
                  onClick={() => document.getElementById("existing-case-pdf-input")?.click()}
                >
                  <input
                    id="existing-case-pdf-input"
                    type="file"
                    accept="application/pdf"
                    style={{ display: "none" }}
                    onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  />
                  {selectedFile ? (
                    <span style={{ color: "#111827" }}>{selectedFile.name}</span>
                  ) : (
                    <span>Choose a PDF file to upload</span>
                  )}
                </div>
              </div>
            </div>

            {uploadSuccess && (
              <div className="alert alert-success mt-3 py-2" style={{ fontSize: "0.9rem" }}>
                <i className="fa-solid fa-circle-check me-2" />Document uploaded successfully.
              </div>
            )}

            <div className="d-flex justify-content-end mt-3">
              <button
                className="btn btn-dark"
                onClick={handleUpload}
                disabled={!selectedFile || isUploading}
              >
                {isUploading ? (
                  <><span className="spinner-border spinner-border-sm me-2" />Uploading...</>
                ) : (
                  <><i className="fa-solid fa-upload me-1" />Upload</>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
