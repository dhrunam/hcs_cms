# Payment Objection Flow - Implementation Summary

## Date: 2026-04-20

---

## Overview

This document summarizes the complete implementation of the payment objection flow in the HCS CMS application. The flow involves advocate-facing pages for paying objections and scrutiny-officer-facing pages for raising and managing objections.

---

## 1. Key Design Decisions

### 1.1 Time-Based Resolution (Not Amount-Based)
The objection resolution is determined by whether a payment was made AFTER the objection was raised, NOT by whether the amount matches. This allows for overpayment scenarios where advocate pays more than demanded.

### 1.2 No Auto-Resolve on Payment Callback
Instead of auto-resolving the objection in the payment callback, we require an explicit "Submit to Scrutiny" action. This is cleaner and gives the advocate control over when to resubmit.

### 1.3 Isolated State
- Payment objection state lives in `PaymentObjection` table, not on `Efiling` model
- Frontend fetches fresh state from API on every page load
- No reliance on URL params for sensitive state (except payment status indicator)

### 1.4 Proper Redirect for Objection Payments
Payments initiated from payment-confirmation page (for objections) are redirected back to that page, not to the default new-filing page.

---

## 2. Backend Changes

### 2.1 New API: Payment Objection Status (`/api/payment/objection-status/`)

**File:** `backend/apps/payment/views.py`

Created new endpoint `PaymentObjectionStatusView` that returns:

```python
{
    "has_objection": True,
    "objection_amount": "56.00",
    "objection_remarks": None,
    "objection_raised_at": "2026-04-20T14:33:54.218799+00:00",
    "can_resubmit": True,
    "payment_resolves_objection": True,
    "resolving_payment": {
        "payment_id": 74,
        "txn_id": "849860",
        "amount": 551.0,
        "payment_datetime": "2026-04-20T08:44:05.752153+00:00",
        "status": "success"
    }
}
```

**Key Logic:**
- Fetches latest PENDING payment objection for the e-filing
- Finds successful payments with `source='objection'` made AFTER the objection was raised
- If such payment exists, `can_resubmit` is True

### 2.2 New API: All Objections for Filing (`/api/v1/efiling/payment-objections/for-filing/`)

**File:** `backend/apps/efiling/views/payment_objection_views.py`

Added new action `for_filing` to `PaymentObjectionViewSet`:

```python
@action(detail=False, methods=['get'])
def for_filing(self, request):
    e_filing_id = request.query_params.get('e_filing')
    objections = PaymentObjection.objects.filter(
        e_filing=efiling
    ).order_by('-raised_at')
    serializer = self.get_serializer(objections, many=True)
    return Response(serializer.data, status=200)
```

### 2.3 Payment Gateway Redirect for Objection

**File:** `backend/apps/payment/views.py` (in `_build_redirect_url`)

Added handling for `source == "objection"`:

```python
elif source == "objection":
    base_redirect_url = pg_params.get(
        "redirect_to_front_end_for_objection_payment",
        pg_params.get("redirect_to_front_end_for_application_fee_paymet_status_page", ""),
    )
```

**File:** `backend/config/settings/base.py`

```python
"redirect_to_front_end_for_objection_payment": os.getenv(
    "PG_OBJECTION_PAYMENT_REDIRECT_URL",
    "http://localhost:4200/advocate/dashboard/efiling/payment-confirmation",
),
```

### 2.4 Removed Efiling Fields

**Files:** `backend/apps/core/models.py`, `backend/apps/efiling/serializers/efiling_serializers.py`, `backend/apps/efiling/views/payment_objection_views.py`

Removed from Efiling model:
- `has_payment_objection`
- `payment_objection_amount`
- `objection_resolved_by_payment`

**Migration:** `backend/apps/core/migrations/0023_remove_efiling_payment_objection_fields.py`

---

## 3. Frontend Changes

### 3.1 Payment Service (`payment.service.ts`)

Added interface and method:

```typescript
export interface PaymentObjectionStatusResponse {
  has_objection: boolean;
  objection_amount: string | null;
  objection_remarks: string | null;
  objection_raised_at: string | null;
  can_resubmit: boolean;
  payment_resolves_objection: boolean;
  resolving_payment: {
    payment_id: number;
    txn_id: string;
    amount: number;
    payment_datetime: string | null;
    status: string;
  } | null;
}

getObjectionStatus(application: string | number): Observable<PaymentObjectionStatusResponse> {
  return this.http.get<PaymentObjectionStatusResponse>(
    `${app_url}/api/payment/objection-status/?application=${application}`,
  );
}
```

### 3.2 Efiling Service (`efiling.services.ts`)

Added method:

```typescript
get_payment_objections(e_filing_id: number): Observable<any> {
  return this.http.get<any>(
    `${app_url}/api/v1/efiling/payment-objections/for-filing/?e_filing=${e_filing_id}`,
  );
}
```

### 3.3 Scrutiny Officer - Details Component (`details.ts`)

Added properties and methods:

```typescript
allObjections: any[] = [];
objectionsSectionCollapsed = true;

toggleObjectionsSection(): void {
  this.objectionsSectionCollapsed = !this.objectionsSectionCollapsed;
}
```

Added to `loadWorkspace()` forkJoin:

```typescript
allObjections: this.efilingService.get_payment_objections(id).pipe(catchError(() => of([]))),
```

### 3.4 Scrutiny Officer - Details Template (`details.html`)

Added collapsible section showing all payment objections:

```html
<!-- All Objections History (Collapsible) -->
<div class="mt-3" *ngIf="allObjections.length > 0">
  <div class="d-flex align-items-center justify-content-between cursor-pointer" 
       (click)="toggleObjectionsSection()">
    <span class="fw-semibold small text-muted">
      <i class="fa-solid fa-clock-rotate-left me-1"></i>
      All Payment Objections ({{ allObjections.length }})
    </span>
    <button type="button" class="btn btn-sm btn-link p-0 text-decoration-none">
      <i class="fa-solid" [ngClass]="objectionsSectionCollapsed ? 'fa-chevron-down' : 'fa-chevron-up'"></i>
    </button>
  </div>
  
  <div class="mt-2" *ngIf="!objectionsSectionCollapsed">
    <div class="alert py-2 small mb-2" *ngFor="let obj of allObjections" 
         [ngClass]="obj.status === 'RESOLVED' ? 'alert-success' : 'alert-warning'">
      <!-- Shows status, amount, remarks, raised_at, resolved_at -->
    </div>
  </div>
</div>
```

Updated "Raise Objection" section to:
- Show "Payment Objection" label (not checkbox) when objection exists
- Display objection details with amount, raised time, and payment info if resolved
- Show "Delete" button for pending objections
- Hide checkbox when objection is active

### 3.5 Advocate - Scrutiny Details Component (`scrutiny-details.ts`)

- Added `objectionStatus: PaymentObjectionStatusResponse | null`
- Added `canResubmitForScrutiny = false`
- Updated `loadDetails()` to call `getObjectionStatus()` API
- Uses `objectionStatus` values instead of filing properties

### 3.6 Advocate - Payment Confirmation Component (`payment-confirmation.ts`)

Key improvements:

1. **State Reset on Load:**

```typescript
ngOnInit(): void {
  this.route.queryParams.subscribe(async (params) => {
    this.filingId = Number(params["id"] || params["application"] || 0) || null;
    this.paymentOutcome = null;
    this.paymentDetails = null;
    this.hasPaymentObjection = false;
    this.objectionResolvedByPayment = null;
    this.resetPaymentForm();
    // ... handle status from params
  });
}
```

2. **Success Flow (redirected from payment gateway):**

```typescript
if (this.paymentOutcome === 'success') {
  const objectionStatusRaw = await firstValueFrom(
    this.paymentService.getObjectionStatus(this.filingId).pipe(...)
  );
  this.objectionResolvedByPayment = objectionStatusRaw?.resolving_payment ?? null;
  await this.loadPaymentDetailsFromBackend();
  return;
}
```

3. **Offline Payment Flow:**

```typescript
this.paymentOutcome = "success";
this.objectionResolvedByPayment = {
  payment_id: response?.id || 0,
  txn_id: response?.txn_id || this.offlineTransactionId.trim(),
  amount: Number(this.paymentObjectionAmount),
  payment_datetime: new Date().toISOString(),
  status: "success",
};
```

4. **Updated Getters:**

```typescript
get isObjectionResolved(): boolean {
  return this.objectionResolvedByPayment !== null;
}

get showPaymentForm(): boolean {
  return this.hasPaymentObjection && 
         !this.isObjectionResolved && 
         this.paymentOutcome !== 'failed' && 
         this.paymentOutcome !== 'success';
}
```

---

## 4. Data Flow

### 4.1 Raising Objection (Scrutiny Officer)

1. Officer navigates to filed-cases details page
2. Checks "Raise Objection on Payment" checkbox
3. Enters court fee amount
4. Clicks "Submit Objection"
5. Backend creates `PaymentObjection` record with status=PENDING
6. E-filing status updated to REJECTED_PAYMENT_OBJECTION

### 4.2 Paying Objection (Advocate)

1. Advocate sees "Payment Objection" on pending scrutiny page
2. Clicks "Pay Now" → navigates to payment-confirmation page
3. Selects online or offline payment
4. **Online:** Submits to payment gateway with `source: "objection"`
5. **Offline:** Submits bank receipt with `source: "objection"` in payload

### 4.3 Checking Objection Status

API `/api/payment/objection-status/?application=X` returns:
- Latest PENDING objection details
- Whether a successful payment exists with `source='objection'` made AFTER the objection time
- If yes → `can_resubmit: true` and `resolving_payment` populated

### 4.4 Resubmitting for Scrutiny (Advocate)

1. Advocate sees "Submit to Scrutiny" button when `can_resubmit: true`
2. Clicks button → calls `resubmit_after_payment_objection()`
3. Backend marks `PaymentObjection` as RESOLVED
4. E-filing status updated to UNDER_SCRUTINY

### 4.5 Deleting Objection (Scrutiny Officer)

1. Officer sees pending objection with "Delete" button
2. Clicks Delete → confirms with Swal dialog
3. Backend deletes `PaymentObjection` record
4. E-filing status updated to UNDER_SCRUTINY

---

## 5. API Endpoints Summary

| Endpoint | Method | Purpose |
|---------|--------|---------|
| `/api/payment/objection-status/` | GET | Check if objection exists and if payment resolves it |
| `/api/v1/efiling/payment-objections/` | GET/POST | List/create payment objections |
| `/api/v1/efiling/payment-objections/for-filing/` | GET | Get all objections for a filing |
| `/api/v1/efiling/payment-objections/reset/` | POST | Delete pending objection |
| `/api/v1/efiling/payment-objections/resubmit/` | POST | Mark objection as resolved, resubmit for scrutiny |

---

## 6. Files Modified

### Backend
- `backend/apps/core/models.py` - Removed payment objection fields
- `backend/apps/core/migrations/0023_remove_efiling_payment_objection_fields.py` - Migration
- `backend/apps/efiling/serializers/efiling_serializers.py` - Removed fields
- `backend/apps/efiling/views/payment_objection_views.py` - Added for_filing action, removed Efiling field updates
- `backend/apps/efiling/urls.py` - Added for_filing route
- `backend/apps/payment/views.py` - Added PaymentObjectionStatusView, updated callback redirect
- `backend/apps/payment/urls.py` - Added objection-status route
- `backend/config/settings/base.py` - Added objection redirect URL config

### Frontend
- `frontend/src/app/services/payment/payment.service.ts` - Added getObjectionStatus()
- `frontend/src/app/services/advocate/efiling/efiling.services.ts` - Added get_payment_objections()
- `frontend/src/app/areas/advocate/dashboard/efiling/payment-confirmation/payment-confirmation.ts` - Fixed state management
- `frontend/src/app/areas/advocate/dashboard/efiling/cases-scrutiny/scrutiny-details/scrutiny-details.ts` - Uses objectionStatus API
- `frontend/src/app/areas/advocate/dashboard/efiling/cases-scrutiny/scrutiny-details/scrutiny-details.html` - Updated UI
- `frontend/src/app/areas/scrutiny-officers/dashboard/filed-cases/details/details.ts` - Added allObjections, toggleObjectionsSection
- `frontend/src/app/areas/scrutiny-officers/dashboard/filed-cases/details/details.html` - Added objections history section

---

## 7. Testing Checklist

- [ ] Scrutiny officer can raise payment objection
- [ ] Advocate sees objection on pending scrutiny page
- [ ] Advocate can pay online and is redirected back to payment-confirmation
- [ ] Payment-confirmation shows "Payment Objection Resolved" on success
- [ ] Advocate can click "Submit to Scrutiny" and case moves to under scrutiny
- [ ] Advocate can pay offline and see success state with "Submit to Scrutiny"
- [ ] Scrutiny officer can see all objections history (collapsible) on details page
- [ ] Scrutiny officer can delete pending objection
- [ ] API correctly identifies payments made before vs after objection time
- [ ] Other payment flows (new filing, IA, document) are unaffected