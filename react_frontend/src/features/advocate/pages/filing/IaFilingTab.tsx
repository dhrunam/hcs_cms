import { useState, useEffect, useMemo, useCallback } from "react";
import { http } from "../../../../shared/lib/http";
import "../../styles/new-filing.css";

type LitigantType = "PETITIONER" | "RESPONDENT" | "APPELLANT";

const LITIGANT_TYPE_OPTIONS: { value: LitigantType; label: string }[] = [
  { value: "PETITIONER", label: "Petitioner" },
  { value: "RESPONDENT", label: "Respondent" },
  { value: "APPELLANT", label: "Appellant" },
];

const IA_COURT_FEE = 10;

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

export default function IaFilingTab() {
  const [filingsWithLitigants, setFilingsWithLitigants] = useState<FilingWithLitigants[]>([]);
  const [isLoadingFilings, setIsLoadingFilings] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [selectedFiling, setSelectedFiling] = useState<any>(null);
  const [litigants, setLitigants] = useState<any[]>([]);
  const [litigantType, setLitigantType] = useState<LitigantType>("PETITIONER");
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);

  /* ── IA form ── */
  const [reliefSought, setReliefSought] = useState("");
  const [createdIa, setCreatedIa] = useState<any>(null);

  /* ── Document upload ── */
  const [docList, setDocList] = useState<any[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [documentType, setDocumentType] = useState("IA");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  /* ── Payment ── */
  const [paymentMode, setPaymentMode] = useState<"online" | "offline">("online");
  const [paymentOutcome, setPaymentOutcome] = useState<"success" | "failed" | null>(null);
  const [offlineTxnId, setOfflineTxnId] = useState("");
  const [offlinePaymentDate, setOfflinePaymentDate] = useState("");
  const [offlineBankReceipt, setOfflineBankReceipt] = useState<File | null>(null);
  const [isSubmittingPayment, setIsSubmittingPayment] = useState(false);

  /* ── Submit ── */
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  /* ── Load filings ── */

  useEffect(() => {
    setIsLoadingFilings(true);
    http.get("/api/v1/efiling/efilings/")
      .then(async (res) => {
        const filings: any[] = res.data?.results ?? res.data ?? [];
        const valid = filings.filter((f: any) => f?.id && f?.e_filing_number);
        const pairs = await Promise.all(
          valid.map(async (filing) => {
            try {
              const lr = await http.get(`/api/v1/efiling/efiling-litigants/?efiling_id=${filing.id}`);
              return { filing, litigants: lr.data?.results ?? lr.data ?? [] };
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

  /* ── Filtered filings ── */

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

  /* ── Select filing ── */

  const selectFiling = useCallback(async (item: FilingWithLitigants) => {
    setSelectedFiling(item.filing);
    setIsDropdownOpen(false);
    setLitigants(item.litigants);
    setCreatedIa(null);
    setDocList([]);
    setPaymentOutcome(null);
    setSubmitError(null);
    setIsLoadingDetails(true);
    try {
      const dr = await http.get(`/api/v1/efiling/efiling-documents/?efiling_id=${item.filing.id}`);
      setDocList(dr.data?.results ?? dr.data ?? []);
    } catch {}
    setIsLoadingDetails(false);
  }, []);

  const getSelectedLabel = () => {
    if (!selectedFiling) return "";
    const item = filingsWithLitigants.find((x) => x.filing.id === selectedFiling.id);
    return `${selectedFiling.e_filing_number} (${selectedFiling.case_type?.type_name || "N/A"})${item ? " — " + getLitigantLabel(item) : ""}`;
  };

  const litigantTypeLabel = () => {
    return LITIGANT_TYPE_OPTIONS.find((o) => o.value === litigantType)?.label || litigantType;
  };

  const petitioners = litigants.filter((l) => l.is_petitioner);
  const respondents = litigants.filter((l) => !l.is_petitioner);

  /* ── Create/update IA ── */

  const handleSaveIa = useCallback(async () => {
    if (!selectedFiling || !reliefSought.trim()) {
      setSubmitError("Please fill in the relief sought.");
      return;
    }
    setIsSubmitting(true);
    setSubmitError(null);
    const fd = new FormData();
    fd.append("e_filing_id", String(selectedFiling.id));
    fd.append("relief_sought", reliefSought);
    fd.append("litigant_type", litigantType);
    try {
      let res;
      if (createdIa?.id) {
        res = await http.patch(`/api/v1/efiling/ia-filing/ia-filings/${createdIa.id}/`, fd);
      } else {
        res = await http.post("/api/v1/efiling/ia-filing/ia-filings/", fd);
      }
      setCreatedIa(res.data);
    } catch (e: any) {
      const msg = e?.response?.data;
      setSubmitError(typeof msg === "string" ? msg : JSON.stringify(msg) || "Failed to save IA details.");
    } finally {
      setIsSubmitting(false);
    }
  }, [selectedFiling, reliefSought, litigantType, createdIa]);

  /* ── Upload document ── */

  const handleUpload = async () => {
    if (!selectedFile || !selectedFiling) return;
    const iaId = createdIa?.id;
    if (!iaId) {
      if (!window.confirm("You haven't saved the IA yet. Upload anyway against the e-filing?")) return;
    }
    setIsUploading(true);
    const fd = new FormData();
    fd.append("efiling_id", String(selectedFiling.id));
    fd.append("document_type", documentType);
    fd.append("litigant_type", litigantType);
    if (iaId) fd.append("ia_id", String(iaId));
    fd.append("final_document", selectedFile);
    try {
      await http.post("/api/v1/efiling/efiling-documents/", fd);
      const dr = await http.get(`/api/v1/efiling/efiling-documents/?efiling_id=${selectedFiling.id}`);
      setDocList(dr.data?.results ?? dr.data ?? []);
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
      setDocList((prev) => prev.filter((d) => d.id !== id));
    } catch {
      alert("Failed to delete document.");
    }
  };

  /* ── Offline payment ── */

  const handleOfflinePayment = async () => {
    if (!offlineTxnId || !offlinePaymentDate) {
      alert("Please fill in Transaction ID and Payment Date.");
      return;
    }
    setIsSubmittingPayment(true);
    const fd = new FormData();
    if (createdIa?.id) fd.append("ia_id", String(createdIa.id));
    if (selectedFiling?.id) fd.append("efiling_id", String(selectedFiling.id));
    fd.append("payment_mode", "offline");
    fd.append("transaction_id", offlineTxnId);
    fd.append("payment_date", offlinePaymentDate);
    fd.append("court_fee", String(IA_COURT_FEE));
    fd.append("payment_type", "IA Court Fee");
    if (offlineBankReceipt) fd.append("bank_receipt", offlineBankReceipt);
    try {
      await http.post("/api/v1/payment/efiling-payment/", fd);
      setPaymentOutcome("success");
    } catch (e: any) {
      alert(e?.response?.data?.detail || "Payment submission failed.");
    } finally {
      setIsSubmittingPayment(false);
    }
  };

  /* ── Final submit ── */

  const handleFinalSubmit = async () => {
    if (!createdIa?.id) {
      setSubmitError("Please save IA details first.");
      return;
    }
    setIsSubmitting(true);
    setSubmitError(null);
    try {
      await http.patch(`/api/v1/efiling/ia-filing/ia-filings/${createdIa.id}/`, { status: "SUBMITTED" });
      setSubmitSuccess(true);
    } catch (e: any) {
      const msg = e?.response?.data;
      setSubmitError(typeof msg === "string" ? msg : JSON.stringify(msg) || "Submission failed.");
    } finally {
      setIsSubmitting(false);
    }
  };

  /* ── Render ── */

  if (submitSuccess) {
    return (
      <div className="card border-0 p-4 text-center">
        <div style={{ fontSize: 48 }}>✅</div>
        <h4 className="mt-3">IA Filing Submitted!</h4>
        {createdIa?.ia_number && <p className="text-muted">IA Number: <strong>{createdIa.ia_number}</strong></p>}
        <p className="text-muted">Your IA has been submitted successfully.</p>
        <button
          className="btn btn-outline-dark mt-2"
          onClick={() => {
            setSubmitSuccess(false);
            setSelectedFiling(null);
            setCreatedIa(null);
            setReliefSought("");
            setDocList([]);
            setPaymentOutcome(null);
          }}
        >
          File Another IA
        </button>
      </div>
    );
  }

  return (
    <div className="ia-filing-form">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h5 className="mb-0">New IA Filing</h5>
      </div>

      {submitError && (
        <div className="alert alert-danger py-2 mb-3" style={{ borderRadius: 8, fontSize: "0.9rem" }}>
          {submitError}
        </div>
      )}

      {/* Select E-Filing */}
      <div className="card border-0 shadow-sm mb-4" style={{ borderRadius: 12 }}>
        <div className="card-header bg-dark text-white fw-semibold" style={{ borderRadius: "12px 12px 0 0" }}>
          Select E-Filing
        </div>
        <div className="card-body">
          <div className="row g-3">
            <div className="col-md-12">
              <label className="form-label">Search &amp; Select E-Filing</label>
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
                  <i className="fa-solid fa-chevron-down ms-2" style={{ transform: isDropdownOpen ? "rotate(180deg)" : "none", transition: "transform 0.2s" }} />
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
            </div>
            <div className="col-md-12">
              <label className="form-label" htmlFor="ia-filing-litigant-type">Filing As</label>
              <select
                id="ia-filing-litigant-type"
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
          </div>
        </div>
      </div>

      {/* Filing Details */}
      {selectedFiling && (
        <div className="card border-0 shadow-sm mb-4" style={{ borderRadius: 12 }}>
          <div className="card-header bg-dark text-white fw-semibold" style={{ borderRadius: "12px 12px 0 0" }}>
            Filing Details
          </div>
          {isLoadingDetails ? (
            <div className="card-body text-muted small">Loading details...</div>
          ) : (
            <div className="card-body">
              <div className="row g-3 mb-3" style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, fontSize: "0.9rem" }}>
                <div>
                  <div className="text-muted small">Case Type</div>
                  <div className="fw-semibold">{selectedFiling.case_type?.type_name || "-"}</div>
                </div>
                <div>
                  <div className="text-muted small">E-Filing Number</div>
                  <div className="fw-semibold">{selectedFiling.e_filing_number || "-"}</div>
                </div>
                <div>
                  <div className="text-muted small">Filing as</div>
                  <div className="fw-semibold">{litigantTypeLabel()}</div>
                </div>
              </div>

              {litigants.length > 0 && (
                <div className="mt-4">
                  <label className="text-muted small fw-semibold d-block mb-2">
                    <i className="fa-solid fa-users me-1" />Litigant Details
                  </label>
                  <div style={{ display: "flex", gap: 16 }}>
                    <div style={{ flex: 1 }}>
                      <div className="fw-semibold small mb-1"><i className="fa-solid fa-user-check me-1" />Petitioners</div>
                      {petitioners.length === 0 ? (
                        <div className="text-muted small">No petitioners available.</div>
                      ) : petitioners.map((l) => (
                        <div key={l.id} style={{ fontSize: 13, marginBottom: 4, padding: "6px 10px", background: "#f8fafc", borderRadius: 6 }}>
                          <div className="fw-semibold">{l.name || "-"}</div>
                          <div className="text-muted">{l.contact || "No contact"}</div>
                          {l.address && <div className="text-muted">{l.address}</div>}
                        </div>
                      ))}
                    </div>
                    <div style={{ display: "flex", alignItems: "center", padding: "0 8px", color: "#6b7280", fontWeight: 600 }}>vs</div>
                    <div style={{ flex: 1 }}>
                      <div className="fw-semibold small mb-1"><i className="fa-solid fa-user-xmark me-1" />Respondents</div>
                      {respondents.length === 0 ? (
                        <div className="text-muted small">No respondents available.</div>
                      ) : respondents.map((l) => (
                        <div key={l.id} style={{ fontSize: 13, marginBottom: 4, padding: "6px 10px", background: "#f8fafc", borderRadius: 6 }}>
                          <div className="fw-semibold">{l.name || "-"}</div>
                          <div className="text-muted">{l.contact || "No contact"}</div>
                          {l.address && <div className="text-muted">{l.address}</div>}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Relief Sought */}
      {selectedFiling && (
        <div className="card border-0 shadow-sm mb-4" style={{ borderRadius: 12 }}>
          <div className="card-header bg-dark text-white fw-semibold" style={{ borderRadius: "12px 12px 0 0" }}>
            Relief Sought
          </div>
          <div className="card-body">
            <label className="form-label">Relief Sought <small className="text-danger">*</small></label>
            <textarea
              className="form-control"
              rows={5}
              placeholder="Enter the relief sought in this IA application..."
              value={reliefSought}
              onChange={(e) => setReliefSought(e.target.value)}
              style={{ borderRadius: 12, padding: "10px 15px", border: "1px solid #d1d5db", fontSize: "0.95rem", width: "100%" }}
            />
            <div className="d-flex justify-content-end mt-3">
              <button
                type="button"
                className="btn btn-dark"
                onClick={handleSaveIa}
                disabled={isSubmitting || !reliefSought.trim()}
              >
                {isSubmitting ? (
                  <><span className="spinner-border spinner-border-sm me-2" />{createdIa?.id ? "Updating..." : "Saving..."}</>
                ) : (
                  <><i className={`fa-solid ${createdIa?.id ? "fa-pen" : "fa-save"} me-1`} />{createdIa?.id ? "Update IA" : "Save IA"}</>
                )}
              </button>
            </div>
            {createdIa && (
              <div className="alert alert-success mt-3 py-2" style={{ fontSize: "0.9rem" }}>
                <i className="fa-solid fa-circle-check me-2" />
                IA saved successfully.{createdIa.ia_number ? ` IA Number: ${createdIa.ia_number}` : ""}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Upload Documents */}
      {selectedFiling && (
        <div className="card border-0 shadow-sm mb-4" style={{ borderRadius: 12 }}>
          <div className="card-header bg-dark text-white fw-semibold d-flex justify-content-between align-items-center" style={{ borderRadius: "12px 12px 0 0" }}>
            <span>Upload Documents</span>
          </div>
          <div className="card-body">
            {/* Existing docs */}
            {docList.length > 0 && (
              <div className="mb-4">
                <div className="section-title mb-2">Uploaded Documents</div>
                <div className="list-group list-group-flush">
                  {docList.map((doc, i) => (
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
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
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
                <div className="drop-zone" onClick={() => document.getElementById("ia-pdf-input")?.click()}>
                  <input
                    id="ia-pdf-input"
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
              <button className="btn btn-dark" onClick={handleUpload} disabled={!selectedFile || isUploading}>
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

      {/* Payment */}
      {selectedFiling && (
        <div className="card border-0 shadow-sm mb-4" style={{ borderRadius: 12 }}>
          <div className="card-header bg-dark text-white fw-semibold" style={{ borderRadius: "12px 12px 0 0" }}>
            IA Court Fee Payment (₹{IA_COURT_FEE})
          </div>
          <div className="card-body">
            {paymentOutcome === "success" ? (
              <div className="alert alert-success">
                <i className="fa-solid fa-circle-check me-2" />
                IA court fee payment completed successfully.
              </div>
            ) : (
              <>
                <div className="payment-mode-toggle mb-4">
                  <button type="button" className={`payment-mode-btn${paymentMode === "online" ? " active" : ""}`} onClick={() => setPaymentMode("online")}>
                    <i className="fa-solid fa-globe me-2" />Online
                  </button>
                  <button type="button" className={`payment-mode-btn${paymentMode === "offline" ? " active" : ""}`} onClick={() => setPaymentMode("offline")}>
                    <i className="fa-solid fa-money-bill me-2" />Offline
                  </button>
                </div>

                {paymentMode === "online" && (
                  <div className="text-center p-4">
                    <p className="text-muted mb-3">
                      Pay IA court fee of <strong>₹{IA_COURT_FEE}</strong> via the secure payment gateway.
                    </p>
                    <button
                      className="btn btn-dark"
                      disabled={!createdIa?.id}
                      onClick={async () => {
                        if (!createdIa?.id || !selectedFiling) return;
                        try {
                          const res = await http.post("/api/v1/payment/initiate/", {
                            ia_id: createdIa.id,
                            amount: IA_COURT_FEE,
                            payment_type: "IA Court Fee",
                            e_filing_number: selectedFiling.e_filing_number,
                          });
                          const url = res.data?.payment_url || res.data?.redirect_url;
                          if (url) window.location.href = url;
                          else alert("Payment gateway URL not received.");
                        } catch (e: any) {
                          alert(e?.response?.data?.detail || "Payment initiation failed.");
                        }
                      }}
                    >
                      <i className="fa-solid fa-arrow-up-right-from-square me-2" />Pay ₹{IA_COURT_FEE} Online
                    </button>
                    {!createdIa?.id && (
                      <p className="text-muted small mt-2">Save IA details first to enable payment.</p>
                    )}
                  </div>
                )}

                {paymentMode === "offline" && (
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                    <div>
                      <label className="form-label">Transaction ID <small className="text-danger">*</small></label>
                      <input
                        className="form-control"
                        value={offlineTxnId}
                        onChange={(e) => setOfflineTxnId(e.target.value)}
                        style={{ borderRadius: 12, padding: "5px 15px", border: "1px solid #d1d5db" }}
                      />
                    </div>
                    <div>
                      <label className="form-label">Payment Date <small className="text-danger">*</small></label>
                      <input
                        type="date"
                        className="form-control"
                        value={offlinePaymentDate}
                        onChange={(e) => setOfflinePaymentDate(e.target.value)}
                        style={{ borderRadius: 12, padding: "5px 15px", border: "1px solid #d1d5db" }}
                      />
                    </div>
                    <div>
                      <label className="form-label">Bank Receipt (optional)</label>
                      <input
                        type="file"
                        className="form-control"
                        accept=".pdf,image/*"
                        onChange={(e) => setOfflineBankReceipt(e.target.files?.[0] || null)}
                        style={{ borderRadius: 12, padding: "5px 15px", border: "1px solid #d1d5db" }}
                      />
                    </div>
                    <div style={{ display: "flex", alignItems: "flex-end" }}>
                      <button
                        className="btn btn-dark w-100"
                        onClick={handleOfflinePayment}
                        disabled={isSubmittingPayment}
                      >
                        {isSubmittingPayment ? (
                          <><span className="spinner-border spinner-border-sm me-2" />Submitting...</>
                        ) : "Submit Payment"}
                      </button>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {/* Submit */}
      {selectedFiling && (
        <div className="d-flex justify-content-end">
          <button
            className="btn btn-dark"
            disabled={!createdIa?.id || isSubmitting}
            onClick={handleFinalSubmit}
          >
            {isSubmitting ? (
              <><span className="spinner-border spinner-border-sm me-2" />Submitting...</>
            ) : (
              <><i className="fa-solid fa-paper-plane me-2" />Submit IA Filing</>
            )}
          </button>
        </div>
      )}
    </div>
  );
}
