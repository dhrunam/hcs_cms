import { useState, useEffect, useCallback, useRef } from "react";
import { http } from "../../../../shared/lib/http";
import "../../styles/new-filing.css";

/* ─── Types ─────────────────────────────────────────────── */

interface CaseType {
  id: number;
  type_name: string;
}

interface LitigantItem {
  id: number;
  name: string;
  gender?: string;
  age?: string | number;
  email?: string;
  contact?: string;
  address?: string;
  sequence_number?: number;
  is_petitioner: boolean;
  is_organisation?: boolean;
  organisation_name?: string;
  is_diffentially_abled?: boolean;
  organization_detail?: { orgname: string };
}

interface LitigantFormState {
  id: string;
  name: string;
  gender: string;
  age: string;
  email: string;
  contact: string;
  address: string;
  is_organisation: boolean;
  organization: string;
  is_diffentially_abled: boolean;
  sequence_number: string;
}

interface DocItem {
  id: number;
  document_type: string;
  document_indexes?: Array<{ id: number; name: string; file?: string }>;
}

const emptyLitigantForm = (): LitigantFormState => ({
  id: "",
  name: "",
  gender: "",
  age: "",
  email: "",
  contact: "",
  address: "",
  is_organisation: false,
  organization: "",
  is_diffentially_abled: false,
  sequence_number: "",
});

type Step = 1 | 4 | 5 | 6;

/* ─── Sub-component: LitigantForm ───────────────────────── */

function LitigantForm({
  side,
  form,
  organisations,
  onChange,
  onSubmit,
  onUndo,
  isEditing,
}: {
  side: "petitioner" | "respondent";
  form: LitigantFormState;
  organisations: Array<{ id: number; orgname: string }>;
  onChange: (field: keyof LitigantFormState, value: string | boolean) => void;
  onSubmit: () => void;
  onUndo?: () => void;
  isEditing: boolean;
}) {
  const label = side === "petitioner" ? "Petitioner" : "Respondent";
  return (
    <form
      className="form-wrapper"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit();
      }}
    >
      <input type="hidden" value={form.id} />

      <div className="form-group-block">
        <div className="section-title">Details</div>

        <div className="row g-3" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
          {/* Is Organisation */}
          <div style={{ gridColumn: "1 / -1" }}>
            <div className="form-check" style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <input
                type="checkbox"
                className="form-check-input"
                checked={form.is_organisation}
                onChange={(e) => onChange("is_organisation", e.target.checked)}
                id={`${side}-is-organisation`}
              />
              <label className="form-check-label" htmlFor={`${side}-is-organisation`}>
                Is Organisation?
              </label>
            </div>
          </div>

          {/* Organisation select (when is_organisation) */}
          {form.is_organisation && (
            <div>
              <label className="form-label">
                Organisation <small className="text-danger">*</small>
              </label>
              <select
                className="form-control"
                value={form.organization}
                onChange={(e) => onChange("organization", e.target.value)}
              >
                <option value="">Select</option>
                {organisations.map((o) => (
                  <option key={o.id} value={String(o.id)}>
                    {o.orgname}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Individual name (when not is_organisation) */}
          {!form.is_organisation && (
            <div>
              <label className="form-label">
                {label} Name <small className="text-danger">*</small>
              </label>
              <input
                className="form-control"
                value={form.name}
                onChange={(e) => onChange("name", e.target.value)}
                required={!form.is_organisation}
              />
            </div>
          )}

          {/* Gender (when not is_organisation) */}
          {!form.is_organisation && (
            <div>
              <label className="form-label">
                Gender <small className="text-danger">*</small>
              </label>
              <select
                className="form-control"
                value={form.gender}
                onChange={(e) => onChange("gender", e.target.value)}
                required={!form.is_organisation}
              >
                <option value="">Select</option>
                <option value="M">Male</option>
                <option value="F">Female</option>
                <option value="O">Other</option>
              </select>
            </div>
          )}

          {/* Age (when not is_organisation) */}
          {!form.is_organisation && (
            <div>
              <label className="form-label">
                Age <small className="text-danger">*</small>
              </label>
              <input
                type="number"
                className="form-control"
                value={form.age}
                onChange={(e) => onChange("age", e.target.value)}
                required={!form.is_organisation}
              />
            </div>
          )}

          {/* Differently Abled (when not is_organisation) */}
          {!form.is_organisation && (
            <div style={{ display: "flex", alignItems: "flex-end" }}>
              <div className="form-check" style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <input
                  type="checkbox"
                  className="form-check-input"
                  checked={form.is_diffentially_abled}
                  onChange={(e) => onChange("is_diffentially_abled", e.target.checked)}
                />
                <label className="form-check-label">Differently Abled</label>
              </div>
            </div>
          )}

          {/* Email */}
          <div>
            <label className="form-label">Email</label>
            <input
              type="email"
              className="form-control"
              value={form.email}
              onChange={(e) => onChange("email", e.target.value)}
            />
          </div>

          {/* Contact */}
          <div>
            <label className="form-label">Mobile No</label>
            <input
              type="tel"
              className="form-control"
              inputMode="numeric"
              pattern="[0-9]{10}"
              maxLength={10}
              value={form.contact}
              onChange={(e) => onChange("contact", e.target.value)}
            />
          </div>

          {/* Address */}
          <div style={{ gridColumn: "1 / -1" }}>
            <label className="form-label">
              Address <small className="text-danger">*</small>
            </label>
            <textarea
              className="form-control"
              rows={2}
              value={form.address}
              onChange={(e) => onChange("address", e.target.value)}
              required
            />
          </div>
        </div>

        <div className="litigant-form-actions">
          <button type="submit" className="btn btn-primary">
            <i className={isEditing ? "fa-solid fa-pen me-1" : "fa-regular fa-save me-1"} />
            {isEditing ? `Update ${label}` : "Submit"}
          </button>
          {isEditing && onUndo && (
            <button type="button" className="btn btn-sm btn-outline-secondary" onClick={onUndo}>
              <i className="fa-solid fa-rotate-left me-1" />
              Undo
            </button>
          )}
        </div>
      </div>
    </form>
  );
}

/* ─── Sub-component: LitigantPanel ──────────────────────── */

function LitigantPanel({
  side,
  litigants,
  form,
  organisations,
  showForm,
  onChangeForm,
  onSubmitForm,
  onUndo,
  onEdit,
  onDelete,
  onStartNew,
}: {
  side: "petitioner" | "respondent";
  litigants: LitigantItem[];
  form: LitigantFormState;
  organisations: Array<{ id: number; orgname: string }>;
  showForm: boolean;
  onChangeForm: (field: keyof LitigantFormState, value: string | boolean) => void;
  onSubmitForm: () => void;
  onUndo: () => void;
  onEdit: (item: LitigantItem) => void;
  onDelete: (id: number) => void;
  onStartNew: () => void;
}) {
  const label = side === "petitioner" ? "Petitioner(s)" : "Respondent(s)";
  const isEditing = !!form.id;

  return (
    <div className={`litigant-panel ${side === "petitioner" ? "petitioner-panel" : "respondent-panel"}`}>
      <div className="litigant-panel-header">
        <div className="litigant-panel-title">
          <div className="litigant-title-text">{label}</div>
        </div>
        <span className="litigant-count">{litigants.length}</span>
      </div>

      {litigants.length === 0 && !showForm && (
        <div className="empty-state">
          No {side} added yet. Click below to add one.
        </div>
      )}

      {litigants.map((item) => (
        <div key={item.id} className="litigant-item">
          <div className="litigant-item-top">
            <div>
              <div className="litigant-name">
                {item.sequence_number != null ? `${item.sequence_number}. ` : ""}
                {item.organization_detail?.orgname || item.name || "-"}
              </div>
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <button
                type="button"
                className="btn btn-sm btn-primary"
                onClick={() => onEdit(item)}
                style={{ display: "flex", alignItems: "center", gap: 4 }}
              >
                <i className="fa-solid fa-pen-to-square" />
              </button>
              <button
                type="button"
                className="btn btn-sm btn-danger"
                onClick={() => onDelete(item.id)}
                style={{ display: "flex", alignItems: "center", gap: 4 }}
              >
                <i className="fa-regular fa-trash-can" />
              </button>
            </div>
          </div>
          <div className="litigant-info-grid">
            {item.gender && <div><strong>Gender:</strong> {item.gender === "M" ? "Male" : item.gender === "F" ? "Female" : "Other"}</div>}
            {item.age && <div><strong>Age:</strong> {item.age}</div>}
            <div><strong>Email:</strong> {item.email || "-"}</div>
            <div><strong>Mobile:</strong> {item.contact || "-"}</div>
            {item.address && <div style={{ gridColumn: "1 / -1" }}><strong>Address:</strong> {item.address}</div>}
          </div>
        </div>
      ))}

      {litigants.length > 0 && !showForm && (
        <div style={{ textAlign: "center", marginTop: 8 }}>
          <button type="button" className="litigant-add-btn" onClick={onStartNew}>
            + Add {side === "petitioner" ? "Petitioner" : "Respondent"}
          </button>
        </div>
      )}

      {(showForm || litigants.length === 0) && (
        <div className="litigant-form-slot">
          <LitigantForm
            side={side}
            form={form}
            organisations={organisations}
            onChange={onChangeForm}
            onSubmit={onSubmitForm}
            onUndo={onUndo}
            isEditing={isEditing}
          />
        </div>
      )}
    </div>
  );
}

/* ─── Main Component ─────────────────────────────────────── */

export default function NewFilingTab() {
  const [step, setStep] = useState<Step>(1);
  const [filingId, setFilingId] = useState<number | null>(null);
  const [eFilingNumber, setEFilingNumber] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /* ── Case types ── */
  const [caseTypes, setCaseTypes] = useState<CaseType[]>([]);
  const [selectedCaseType, setSelectedCaseType] = useState("");

  /* ── Organisations ── */
  const [organisations, setOrganisations] = useState<Array<{ id: number; orgname: string }>>([]);

  /* ── Litigants ── */
  const [litigantList, setLitigantList] = useState<LitigantItem[]>([]);
  const [petitionerForm, setPetitionerForm] = useState<LitigantFormState>(emptyLitigantForm());
  const [respondentForm, setRespondentForm] = useState<LitigantFormState>(emptyLitigantForm());
  const [showPetitionerForm, setShowPetitionerForm] = useState(true);
  const [showRespondentForm, setShowRespondentForm] = useState(true);

  /* ── Documents ── */
  const [docList, setDocList] = useState<DocItem[]>([]);
  const [isUploadingDoc, setIsUploadingDoc] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadDocType, setUploadDocType] = useState("New Filing");

  /* ── Payment ── */
  const [paymentMode, setPaymentMode] = useState<"online" | "offline">("online");
  const [courtFeeAmount, setCourtFeeAmount] = useState("");
  const [offlineTxnId, setOfflineTxnId] = useState("");
  const [offlinePaymentDate, setOfflinePaymentDate] = useState("");
  const [offlineBankReceipt, setOfflineBankReceipt] = useState<File | null>(null);
  const [paymentOutcome, setPaymentOutcome] = useState<"success" | "failed" | null>(null);
  const [isSubmittingPayment, setIsSubmittingPayment] = useState(false);
  const [paymentDetails, setPaymentDetails] = useState<Record<string, string>>({});

  /* ── Declaration ── */
  const [isDeclarationChecked, setIsDeclarationChecked] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  /* ── Toast ── */
  const [toastMsg, setToastMsg] = useState<string | null>(null);
  const toastTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const showToast = useCallback((message: string) => {
    if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    setToastMsg(message);
    toastTimerRef.current = setTimeout(() => setToastMsg(null), 3500);
  }, []);

  /* ─── Load data on mount ───────────────────────────────── */

  useEffect(() => {
    http.get("/api/v1/master/case-types/").then((res) => {
      const data = (res as any).data;
      setCaseTypes(Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : []);
    }).catch(() => {});

    http.get("/api/v1/master/org-names/").then((res) => {
      const data = (res as any).data;
      setOrganisations(Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : []);
    }).catch(() => {});
  }, []);

  /* ─── Load documents when filingId available ─────────────── */

  const loadDocuments = useCallback(async (id: number) => {
    try {
      const res = await http.get(`/api/v1/efiling/efiling-documents/?efiling_id=${id}`);
      const data = res.data;
      setDocList(Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : []);
    } catch {}
  }, []);

  const loadLitigants = useCallback(async (id: number) => {
    try {
      const res = await http.get(`/api/v1/efiling/efiling-litigants/?efiling_id=${id}`);
      const data = res.data;
      const list: LitigantItem[] = Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : [];
      setLitigantList(list);
      /* Hide form panels if at least one litigant of each type exists */
      const hasPetitioner = list.some((l) => l.is_petitioner);
      const hasRespondent = list.some((l) => !l.is_petitioner);
      if (hasPetitioner) setShowPetitionerForm(false);
      if (hasRespondent) setShowRespondentForm(false);
    } catch {}
  }, []);

  /* ─── Ensure filing exists before saving a litigant ─────── */

  const ensureFiling = useCallback(async (): Promise<number | null> => {
    if (filingId) return filingId;
    if (!selectedCaseType) {
      setError("Please select a case category first.");
      return null;
    }
    const fd = new FormData();
    fd.append("bench", "High Court Of Sikkim");
    fd.append("case_type", selectedCaseType);
    fd.append("petitioner_name", "-");
    fd.append("petitioner_contact", "0000000000");
    try {
      const res = await http.post("/api/v1/efiling/efilings/", fd);
      const id = res.data.id as number;
      const num = res.data.e_filing_number as string;
      setFilingId(id);
      setEFilingNumber(num || "");
      return id;
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Failed to create filing. Please try again.");
      return null;
    }
  }, [filingId, selectedCaseType]);

  /* ─── Litigant helpers ───────────────────────────────────── */

  const petitioners = litigantList.filter((l) => l.is_petitioner);
  const respondents = litigantList.filter((l) => !l.is_petitioner);

  const hasRequiredLitigants = petitioners.length >= 1 && respondents.length >= 1;
  const isStep1Completed = Boolean(filingId) && hasRequiredLitigants;

  const nextSequenceNumber = (isPetitioner: boolean): number => {
    const filtered = litigantList.filter((l) => l.is_petitioner === isPetitioner);
    return filtered.length + 1;
  };

  const handleChangePetitionerForm = (field: keyof LitigantFormState, value: string | boolean) => {
    setPetitionerForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleChangeRespondentForm = (field: keyof LitigantFormState, value: string | boolean) => {
    setRespondentForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleEditLitigant = (item: LitigantItem) => {
    const state: LitigantFormState = {
      id: String(item.id),
      name: item.name || "",
      gender: item.gender || "",
      age: item.age != null ? String(item.age) : "",
      email: item.email || "",
      contact: item.contact || "",
      address: item.address || "",
      is_organisation: item.is_organisation ?? false,
      organization: "",
      is_diffentially_abled: item.is_diffentially_abled ?? false,
      sequence_number: item.sequence_number != null ? String(item.sequence_number) : "",
    };
    if (item.is_petitioner) {
      setPetitionerForm(state);
      setShowPetitionerForm(true);
    } else {
      setRespondentForm(state);
      setShowRespondentForm(true);
    }
  };

  const handleDeleteLitigant = async (id: number) => {
    if (!window.confirm("Delete this litigant?")) return;
    try {
      await http.delete(`/api/v1/efiling/efiling-litigants/${id}/`);
      setLitigantList((prev) => prev.filter((l) => l.id !== id));
    } catch {
      alert("Failed to delete litigant.");
    }
  };

  const buildLitigantFd = (form: LitigantFormState, isPetitioner: boolean, id: number): FormData => {
    const fd = new FormData();
    fd.append("efiling_id", String(id));
    fd.append("is_petitioner", isPetitioner ? "true" : "false"); 
    fd.append("name", form.name);
    fd.append("gender", form.gender);
    fd.append("age", form.age);
    fd.append("email", form.email);
    fd.append("contact", form.contact);
    fd.append("address", form.address);
    fd.append("is_organisation", form.is_organisation ? "true" : "false");
    fd.append("organization", form.organization);
    fd.append("is_diffentially_abled", form.is_diffentially_abled ? "true" : "false");
    fd.append("sequence_number", form.sequence_number || String(nextSequenceNumber(isPetitioner)));
    return fd;
  };

  const handleSubmitLitigant = async (side: "petitioner" | "respondent") => {
    const isPetitioner = side === "petitioner";
    const form = isPetitioner ? petitionerForm : respondentForm;
    setIsSaving(true);
    setError(null);
    const id = await ensureFiling();
    if (!id) { setIsSaving(false); return; }

    const fd = buildLitigantFd(form, isPetitioner, id);
    try {
      if (form.id) {
        // Update
        fd.append("id", form.id);
        await http.put(`/api/v1/efiling/efiling-litigants/${form.id}/`, fd);
      } else {
        // Create
        await http.post("/api/v1/efiling/efiling-litigants/", fd);
      }
      await loadLitigants(id);
      if (isPetitioner) {
        setPetitionerForm(emptyLitigantForm());
        setShowPetitionerForm(false);
      } else {
        setRespondentForm(emptyLitigantForm());
        setShowRespondentForm(false);
      }
    } catch (e: any) {
      const msg = e?.response?.data;
      setError(typeof msg === "string" ? msg : JSON.stringify(msg) || "Failed to save litigant.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleUndoLitigant = (side: "petitioner" | "respondent") => {
    if (side === "petitioner") {
      setPetitionerForm(emptyLitigantForm());
      setShowPetitionerForm(petitioners.length === 0);
    } else {
      setRespondentForm(emptyLitigantForm());
      setShowRespondentForm(respondents.length === 0);
    }
  };

  /* ─── Document upload ────────────────────────────────────── */

  const handleUploadDoc = async () => {
    if (!selectedFile || !filingId) return;
    setIsUploadingDoc(true);
    const fd = new FormData();
    fd.append("efiling_id", String(filingId));
    fd.append("document_type", uploadDocType);
    fd.append("final_document", selectedFile);
    try {
      await http.post("/api/v1/efiling/efiling-documents/", fd);
      await loadDocuments(filingId);
      setSelectedFile(null);
      setUploadDocType("New Filing");
    } catch (e: any) {
      alert(e?.response?.data?.detail || "Document upload failed.");
    } finally {
      setIsUploadingDoc(false);
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

  /* ─── Payment ─────────────────────────────────────────────── */

  const handleOfflinePaymentSubmit = async () => {
    if (!filingId) return;
    if (!offlineTxnId || !offlinePaymentDate) {
      alert("Please fill in Transaction ID and Payment Date.");
      return;
    }
    setIsSubmittingPayment(true);
    const fd = new FormData();
    fd.append("efiling_id", String(filingId));
    fd.append("payment_mode", "offline");
    fd.append("transaction_id", offlineTxnId);
    fd.append("payment_date", offlinePaymentDate);
    fd.append("court_fee", courtFeeAmount);
    if (offlineBankReceipt) fd.append("bank_receipt", offlineBankReceipt);
    try {
      await http.post("/api/v1/payment/efiling-payment/", fd);
      setPaymentOutcome("success");
      setPaymentDetails({ txnId: offlineTxnId, paymentDate: offlinePaymentDate, amount: courtFeeAmount, paymentMode: "offline" });
    } catch (e: any) {
      alert(e?.response?.data?.detail || "Payment submission failed.");
    } finally {
      setIsSubmittingPayment(false);
    }
  };

  /* ─── Final submit ────────────────────────────────────────── */

  const handleFinalSubmit = async () => {
    if (!filingId) return;
    setIsSubmitting(true);
    const fd = new FormData();
    fd.append("is_draft", "false");
    try {
      await http.patch(`/api/v1/efiling/efilings/${filingId}/`, fd);
      setSubmitSuccess(true);
    } catch (e: any) {
      alert(e?.response?.data?.detail || "Submission failed.");
    } finally {
      setIsSubmitting(false);
    }
  };

  /* ─── Step navigation ────────────────────────────────────── */

  const goToStep = (s: Step) => {
    if (s === 4 && !filingId) { setError("Please complete Case Info first."); return; }
    if (s === 5 && !filingId) { setError("Please complete Case Info first."); return; }
    if (s === 6 && !filingId) { setError("Please complete Case Info first."); return; }
    setError(null);
    setStep(s);
    if (s === 4 && filingId) loadDocuments(filingId);
  };

  const handleNext = () => {
    if (!hasRequiredLitigants) { setError("Please add at least one petitioner and one respondent."); return; }
    if (!filingId) { setError("Save at least one litigant first to create the filing."); return; }
    setError(null);
    loadDocuments(filingId);
    setStep(4);
  };

  useEffect(() => {
    if (!isStep1Completed && step !== 1) {
      setStep(1);
    }
  }, [isStep1Completed, step]);

  /* ─── Render ─────────────────────────────────────────────── */

  if (submitSuccess) {
    return (
      <div className="card border-0 p-4 text-center">
        <div style={{ fontSize: 48 }}>✅</div>
        <h4 className="mt-3">E-Filing Submitted!</h4>
        <p className="text-muted">E-Filing Number: <strong>{eFilingNumber}</strong></p>
        <p className="text-muted">Your filing has been submitted successfully and is pending scrutiny.</p>
        <button className="btn btn-outline-dark mt-2" onClick={() => { setSubmitSuccess(false); setFilingId(null); setStep(1); setLitigantList([]); setDocList([]); setEFilingNumber(""); setSelectedCaseType(""); setPetitionerForm(emptyLitigantForm()); setRespondentForm(emptyLitigantForm()); setShowPetitionerForm(true); setShowRespondentForm(true); setPaymentOutcome(null); setIsDeclarationChecked(false); }}>
          Start New Filing
        </button>
      </div>
    );
  }

  return (
    <div className="card border-0 p-4">
      <header>
        <h4 className="mb-3">New Filing</h4>
        {eFilingNumber && (
          <div className="filing-meta mb-3">
            <span className="badge bg-dark filing-number-tag">E-Filing No: {eFilingNumber}</span>
          </div>
        )}
        <hr />
      </header>

      {error && (
        <div className="alert alert-danger py-2 mb-3" style={{ borderRadius: 8, fontSize: "0.9rem" }}>
          {error}
        </div>
      )}

      {toastMsg && (
        <div className="filing-toast">
          <i className="fa-solid fa-triangle-exclamation me-2" />
          {toastMsg}
        </div>
      )}

      <div className="accordion new-filing-accordion" id="newFilingAccordion">
        {/* ── Step 1: Case Info ── */}
        <div className="accordion-item">
          <h2 className="accordion-header">
            <button
              className={`accordion-button${step !== 1 ? " collapsed" : ""}`}
              type="button"
              onClick={() => { setError(null); setStep(1); }}
              aria-expanded={step === 1}
            >
              <i className="fa-solid fa-users me-2" />
              Case Info
            </button>
          </h2>

          <div className={`accordion-collapse collapse${step === 1 ? " show" : ""}`}>
            <div className="accordion-body">
              {/* Case Category */}
              <div className="mb-4">
                <label className="form-label fw-semibold">
                  Case Category <small className="text-danger">*</small>
                </label>
                {filingId ? (
                  <input
                    className="form-control"
                    value={caseTypes.find((c) => String(c.id) === selectedCaseType)?.type_name || selectedCaseType}
                    readOnly
                    disabled
                    style={{ borderRadius: 12, padding: "5px 15px", border: "1px solid #d1d5db", fontSize: "0.99rem", background: "#f9fafb" }}
                  />
                ) : (
                  <select
                    className="form-control"
                    value={selectedCaseType}
                    onChange={(e) => setSelectedCaseType(e.target.value)}
                    style={{ borderRadius: 12, padding: "5px 15px", border: "1px solid #d1d5db", fontSize: "0.99rem", height: 38 }}
                  >
                    <option value="">Select</option>
                    {caseTypes.map((c) => (
                      <option key={c.id} value={String(c.id)}>{c.type_name}</option>
                    ))}
                  </select>
                )}
              </div>

              {/* Litigant warning */}
              {!hasRequiredLitigants && (
                <div className="alert alert-warning px-2 py-1 mb-3" style={{ fontSize: "0.85rem" }}>
                  Please add at least one petitioner and one respondent before moving forward.
                </div>
              )}

              {/* Litigants section */}
              <div className="litigant-split-view">
                <div className="litigant-side">
                  <LitigantPanel
                    side="petitioner"
                    litigants={petitioners}
                    form={petitionerForm}
                    organisations={organisations}
                    showForm={showPetitionerForm}
                    onChangeForm={handleChangePetitionerForm}
                    onSubmitForm={() => handleSubmitLitigant("petitioner")}
                    onUndo={() => handleUndoLitigant("petitioner")}
                    onEdit={handleEditLitigant}
                    onDelete={handleDeleteLitigant}
                    onStartNew={() => { setPetitionerForm(emptyLitigantForm()); setShowPetitionerForm(true); }}
                  />
                </div>

                <div className="litigant-vs-col">
                  <div className="litigant-vs-badge fw-lighter">V/S</div>
                </div>

                <div className="litigant-side">
                  <LitigantPanel
                    side="respondent"
                    litigants={respondents}
                    form={respondentForm}
                    organisations={organisations}
                    showForm={showRespondentForm}
                    onChangeForm={handleChangeRespondentForm}
                    onSubmitForm={() => handleSubmitLitigant("respondent")}
                    onUndo={() => handleUndoLitigant("respondent")}
                    onEdit={handleEditLitigant}
                    onDelete={handleDeleteLitigant}
                    onStartNew={() => { setRespondentForm(emptyLitigantForm()); setShowRespondentForm(true); }}
                  />
                </div>
              </div>

              {isSaving && (
                <div className="text-muted mt-2" style={{ fontSize: "0.85rem" }}>
                  <span className="spinner-border spinner-border-sm me-1" />
                  Saving...
                </div>
              )}

              <div className="d-flex justify-content-end mt-4">
                <button
                  className="btn btn-outline-dark"
                  onClick={handleNext}
                  disabled={!hasRequiredLitigants}
                >
                  Next <i className="fa-solid fa-chevron-right ms-2" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* ── Step 4: Pleadings / Upload ── */}
        <div className="accordion-item">
          <h2 className="accordion-header">
            <button
              className={`accordion-button${step !== 4 ? " collapsed" : ""}${!isStep1Completed ? " step-locked" : ""}`}
              type="button"
              onClick={() => {
                if (!isStep1Completed) { showToast("Please complete Case Info with at least one petitioner and one respondent first."); return; }
                goToStep(4);
              }}
              aria-expanded={step === 4}
            >
              <i className="fa-solid fa-file-pdf me-2" />
              Pleadings
              {!isStep1Completed && <i className="fa-solid fa-lock step-lock-icon" />}
            </button>
          </h2>

          <div className={`accordion-collapse collapse${step === 4 ? " show" : ""}`}>
            <div className="accordion-body">
              <div className="preview-page rounded-3 p-3">
                <h5 className="section-title text-start">Upload</h5>
                <p className="text-muted text-start mb-4" style={{ fontSize: "0.9rem" }}>
                  Please attach all required documents before submitting the e-filing.
                </p>

                {/* Existing documents list */}
                {docList.length > 0 && (
                  <div className="mb-4">
                    <div className="card shadow-sm border-0">
                      <div className="list-group list-group-flush">
                        {docList.map((doc, i) => (
                          <div key={doc.id} className="list-group-item doc-slot-row">
                            <div className="d-flex justify-content-between align-items-start gap-2">
                              <div className="text-start">
                                <div className="fw-semibold">{i + 1}. {doc.document_type}</div>
                              </div>
                              <button
                                className="btn btn-sm btn-outline-danger"
                                onClick={() => handleDeleteDoc(doc.id)}
                              >
                                <i className="fa fa-trash" /> delete
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* Upload form */}
                {filingId && (
                  <div className="card border-0 shadow-sm p-3 mb-4">
                    <h6 className="section-title mb-3">Upload Document</h6>
                    <div className="row g-3" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                      <div>
                        <label className="form-label">Document Type</label>
                        <input
                          className="form-control"
                          value={uploadDocType}
                          onChange={(e) => setUploadDocType(e.target.value)}
                          style={{ borderRadius: 12, padding: "5px 15px", border: "1px solid #d1d5db", fontSize: "0.99rem" }}
                        />
                      </div>
                      <div>
                        <label className="form-label">Select PDF</label>
                        <div
                          className="drop-zone"
                          onClick={() => document.getElementById("new-filing-pdf-input")?.click()}
                        >
                          <input
                            id="new-filing-pdf-input"
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
                    <div className="d-flex justify-content-end mt-3">
                      <button
                        className="btn btn-dark"
                        onClick={handleUploadDoc}
                        disabled={!selectedFile || isUploadingDoc}
                      >
                        {isUploadingDoc ? (
                          <><span className="spinner-border spinner-border-sm me-2" />Uploading...</>
                        ) : (
                          <><i className="fa-solid fa-upload me-1" />Upload</>
                        )}
                      </button>
                    </div>
                  </div>
                )}

                {!filingId && (
                  <div className="alert alert-info py-2" style={{ fontSize: "0.9rem" }}>
                    Complete Step 1 first to enable document upload.
                  </div>
                )}

                <div className="d-flex justify-content-between mt-4">
                  <button className="btn btn-outline-secondary" onClick={() => setStep(1)}>
                    <i className="fa-solid fa-chevron-left me-2" />Back
                  </button>
                  <button
                    className="btn btn-outline-dark"
                    onClick={() => goToStep(5)}
                    disabled={!filingId}
                  >
                    Next <i className="fa-solid fa-chevron-right ms-2" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ── Step 5: Payment ── */}
        <div className="accordion-item">
          <h2 className="accordion-header">
            <button
              className={`accordion-button${step !== 5 ? " collapsed" : ""}${!isStep1Completed ? " step-locked" : ""}`}
              type="button"
              onClick={() => {
                if (!isStep1Completed) { showToast("Please complete Case Info with at least one petitioner and one respondent first."); return; }
                goToStep(5);
              }}
              aria-expanded={step === 5}
            >
              <i className="fa-solid fa-credit-card me-2" />
              Payment
              {!isStep1Completed && <i className="fa-solid fa-lock step-lock-icon" />}
            </button>
          </h2>

          <div className={`accordion-collapse collapse${step === 5 ? " show" : ""}`}>
            <div className="accordion-body">
              {paymentOutcome === "success" ? (
                <div className="alert alert-success">
                  <i className="fa-solid fa-circle-check me-2" />
                  Payment successful!{" "}
                  {paymentDetails.txnId && <>Transaction ID: <strong>{paymentDetails.txnId}</strong></>}
                  <div className="mt-2">
                    <button className="btn btn-outline-dark btn-sm" onClick={() => goToStep(6)}>
                      Proceed to Submit <i className="fa-solid fa-chevron-right ms-1" />
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <h5 className="section-title mb-4">Court Fee Payment</h5>

                  <div className="mb-3">
                    <label className="form-label fw-semibold">Court Fee Amount (₹)</label>
                    <input
                      type="number"
                      className="form-control"
                      value={courtFeeAmount}
                      onChange={(e) => setCourtFeeAmount(e.target.value)}
                      placeholder="Enter amount"
                      style={{ borderRadius: 12, padding: "5px 15px", border: "1px solid #d1d5db", maxWidth: 240 }}
                    />
                  </div>

                  <div className="payment-mode-toggle mb-4">
                    <button
                      type="button"
                      className={`payment-mode-btn${paymentMode === "online" ? " active" : ""}`}
                      onClick={() => setPaymentMode("online")}
                    >
                      <i className="fa-solid fa-globe me-2" />Online
                    </button>
                    <button
                      type="button"
                      className={`payment-mode-btn${paymentMode === "offline" ? " active" : ""}`}
                      onClick={() => setPaymentMode("offline")}
                    >
                      <i className="fa-solid fa-money-bill me-2" />Offline
                    </button>
                  </div>

                  {paymentMode === "online" && (
                    <div className="card border-0 shadow-sm p-4 text-center">
                      <p className="text-muted mb-3">
                        You will be redirected to the secure payment gateway to complete your court fee payment.
                      </p>
                      <button
                        className="btn btn-dark"
                        disabled={!courtFeeAmount || !filingId}
                        onClick={async () => {
                          if (!filingId) return;
                          try {
                            const res = await http.post("/api/v1/payment/initiate/", {
                              efiling_id: filingId,
                              amount: courtFeeAmount,
                              payment_type: "Court Fee",
                            });
                            const url = res.data?.payment_url || res.data?.redirect_url;
                            if (url) window.location.href = url;
                            else alert("Payment gateway URL not received.");
                          } catch (e: any) {
                            alert(e?.response?.data?.detail || "Payment initiation failed.");
                          }
                        }}
                      >
                        <i className="fa-solid fa-arrow-up-right-from-square me-2" />
                        Pay Online
                      </button>
                    </div>
                  )}

                  {paymentMode === "offline" && (
                    <div className="card border-0 shadow-sm p-4">
                      <div className="row g-3" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
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
                      </div>
                      <div className="d-flex justify-content-end mt-3">
                        <button
                          className="btn btn-dark"
                          onClick={handleOfflinePaymentSubmit}
                          disabled={isSubmittingPayment}
                        >
                          {isSubmittingPayment ? (
                            <><span className="spinner-border spinner-border-sm me-2" />Submitting...</>
                          ) : (
                            "Submit Payment"
                          )}
                        </button>
                      </div>
                    </div>
                  )}
                </>
              )}

              <div className="d-flex justify-content-between mt-4">
                <button className="btn btn-outline-secondary" onClick={() => setStep(4)}>
                  <i className="fa-solid fa-chevron-left me-2" />Back
                </button>
                {paymentOutcome !== "success" && (
                  <button className="btn btn-link text-muted btn-sm" onClick={() => goToStep(6)}>
                    Skip for now
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* ── Step 6: E-File ── */}
        <div className="accordion-item">
          <h2 className="accordion-header">
            <button
              className={`accordion-button${step !== 6 ? " collapsed" : ""}${!isStep1Completed ? " step-locked" : ""}`}
              type="button"
              onClick={() => {
                if (!isStep1Completed) { showToast("Please complete Case Info with at least one petitioner and one respondent first."); return; }
                goToStep(6);
              }}
              aria-expanded={step === 6}
            >
              <i className="fa-solid fa-paper-plane me-2" />
              E-File
              {!isStep1Completed && <i className="fa-solid fa-lock step-lock-icon" />}
            </button>
          </h2>

          <div className={`accordion-collapse collapse${step === 6 ? " show" : ""}`}>
            <div className="accordion-body">
              <div className="mb-4">
                <h5 className="section-title mb-3">Review & Submit</h5>
                {filingId && (
                  <div className="card border-0 shadow-sm p-3 mb-4">
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, fontSize: "0.9rem" }}>
                      <div>
                        <div className="text-muted small">E-Filing Number</div>
                        <div className="fw-semibold">{eFilingNumber || "-"}</div>
                      </div>
                      <div>
                        <div className="text-muted small">Case Type</div>
                        <div className="fw-semibold">{caseTypes.find((c) => String(c.id) === selectedCaseType)?.type_name || "-"}</div>
                      </div>
                      <div>
                        <div className="text-muted small">Petitioners</div>
                        <div className="fw-semibold">{petitioners.length}</div>
                      </div>
                      <div>
                        <div className="text-muted small">Respondents</div>
                        <div className="fw-semibold">{respondents.length}</div>
                      </div>
                      <div>
                        <div className="text-muted small">Documents Uploaded</div>
                        <div className="fw-semibold">{docList.length}</div>
                      </div>
                      <div>
                        <div className="text-muted small">Payment</div>
                        <div className={`fw-semibold ${paymentOutcome === "success" ? "text-success" : "text-warning"}`}>
                          {paymentOutcome === "success" ? "Completed" : "Pending"}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                <div className="form-check mb-4" style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
                  <input
                    type="checkbox"
                    className="form-check-input mt-1"
                    id="declaration-check"
                    checked={isDeclarationChecked}
                    onChange={(e) => setIsDeclarationChecked(e.target.checked)}
                  />
                  <label className="form-check-label" htmlFor="declaration-check" style={{ fontSize: "0.9rem", lineHeight: 1.5 }}>
                    I hereby declare that all information provided in this e-filing is true, correct, and complete to the best of my knowledge and belief.
                  </label>
                </div>

                <div className="d-flex justify-content-between">
                  <button className="btn btn-outline-secondary" onClick={() => setStep(5)}>
                    <i className="fa-solid fa-chevron-left me-2" />Back
                  </button>
                  <button
                    className={`btn btn-${isDeclarationChecked && filingId ? "dark" : "secondary"}`}
                    disabled={!isDeclarationChecked || !filingId || isSubmitting}
                    onClick={handleFinalSubmit}
                  >
                    {isSubmitting ? (
                      <><span className="spinner-border spinner-border-sm me-2" />Submitting...</>
                    ) : (
                      <><i className="fa-solid fa-paper-plane me-2" />Submit E-Filing</>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
