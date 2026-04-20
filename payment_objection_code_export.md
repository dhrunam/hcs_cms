# Payment Objection Code - Scrutiny Officer & Advocate

## SCRUTINY OFFICER - Raise Payment Objection

### TypeScript (details.ts)

**Variables (add to class):**
```typescript
raisePaymentObjection = false;
directCourtFeeAmount: number | null = null;
isSubmittingPaymentObjection = false;
hasPaymentObjection = false;
paymentObjectionAmount: number | null = null;
objectionResolvedByPayment: any | null = null;
allPayments: any[] = [];
collapsedPayments = new Set<number>();
```

**canSubmitPaymentObjection getter:**
```typescript
get canSubmitPaymentObjection(): boolean {
  return (
    !this.isSubmittingPaymentObjection &&
    this.directCourtFeeAmount !== null &&
    this.directCourtFeeAmount > 0
  );
}
```

**togglePaymentCollapse method:**
```typescript
togglePaymentCollapse(paymentId: number): void {
  if (this.collapsedPayments.has(paymentId)) {
    this.collapsedPayments.delete(paymentId);
  } else {
    this.collapsedPayments.add(paymentId);
  }
}
```

**isPaymentCollapsed method:**
```typescript
isPaymentCollapsed(paymentId: number): boolean {
  return !this.collapsedPayments.has(paymentId);
}
```

**sortedPayments getter:**
```typescript
get sortedPayments(): any[] {
  return [...this.allPayments].sort((a, b) => {
    const dateA = new Date(a.payment_datetime || 0).getTime();
    const dateB = new Date(b.payment_datetime || 0).getTime();
    return dateB - dateA;
  });
}
```

**isPaymentObjectionResolved getter:**
```typescript
get isPaymentObjectionResolved(): boolean {
  return this.objectionResolvedByPayment !== null;
}
```

**getPaymentStatusLabel method:**
```typescript
getPaymentStatusLabel(status: string | null): string {
  if (!status) return 'Unknown';
  const s = status.toLowerCase();
  if (/(success|paid|complete|ok)/i.test(s)) return 'Success';
  if (/failed/i.test(s)) return 'Failed';
  if (/pending|initiated/i.test(s)) return 'Pending';
  if (/offline_submitted|submitted/i.test(s)) return 'Submitted';
  return status;
}
```

**getPaymentStatusClass method:**
```typescript
getPaymentStatusClass(status: string | null): string {
  const label = this.getPaymentStatusLabel(status).toLowerCase();
  if (label.includes('success')) return 'text-success';
  if (label.includes('fail')) return 'text-danger';
  if (label.includes('pending')) return 'text-warning';
  return 'text-muted';
}
```

**submitPaymentObjection() method:**
```typescript
submitPaymentObjection(): void {
  if (!this.filingId || !this.directCourtFeeAmount) {
    this.toastr.error("Please enter a valid court fee amount.");
    return;
  }
  const amount: number = Number(this.directCourtFeeAmount);
  if (!Number.isFinite(amount) || amount <= 0) {
    this.toastr.error("Please enter a valid court fee amount.");
    return;
  }
  this.isSubmittingPaymentObjection = true;
  const filingId = this.filingId;

  Swal.fire({
    title: "Raise Payment Objection?",
    html: `This will reject the case due to incorrect payment. The advocate will be notified to pay the correct court fee of <strong>₹${amount}</strong>.`,
    icon: "warning",
    showCancelButton: true,
    confirmButtonText: "Yes, Raise Objection",
    cancelButtonText: "Cancel",
    confirmButtonColor: "#dc3545",
    cancelButtonColor: "#6c757d",
  }).then((result) => {
    if (!result.isConfirmed) {
      this.isSubmittingPaymentObjection = false;
      return;
    }

    this.efilingService.raise_payment_objection(filingId, amount).subscribe({
      next: (response) => {
        this.isSubmittingPaymentObjection = false;
        this.toastr.success("Payment objection raised. Case has been rejected.");
        this.raisePaymentObjection = false;
        this.directCourtFeeAmount = null;
        this.paymentOutcome = "failed";
        this.hasPaymentObjection = true;
        this.paymentObjectionAmount = amount;
        if (this.filingId) {
          this.loadWorkspace(this.filingId);
        }
      },
      error: (error) => {
        this.isSubmittingPaymentObjection = false;
        this.toastr.error(error?.error?.detail || error?.message || "Failed to raise payment objection.");
      },
    });
  });
}
```

**resetPaymentObjection() method:**
```typescript
resetPaymentObjection(): void {
  if (!this.filingId) return;

  Swal.fire({
    title: "Reset Payment Objection?",
    html: "This will cancel the pending objection and restore the case to under scrutiny. The advocate will not be notified.",
    icon: "warning",
    showCancelButton: true,
    confirmButtonText: "Yes, Reset",
    cancelButtonText: "Cancel",
    confirmButtonColor: "#dc3545",
    cancelButtonColor: "#6c757d",
  }).then((result) => {
    if (!result.isConfirmed) return;

    this.efilingService.reset_payment_objection(this.filingId!).subscribe({
      next: (response) => {
        this.toastr.success("Payment objection has been reset.");
        this.hasPaymentObjection = false;
        this.paymentObjectionAmount = null;
        this.objectionResolvedByPayment = null;
        this.raisePaymentObjection = false;
        if (this.filingId) {
          this.loadWorkspace(this.filingId);
        }
      },
      error: (error) => {
        this.toastr.error(error?.error?.error || error?.message || "Failed to reset payment objection.");
      },
    });
  });
}
```

**In loadWorkspace() - add to forkJoin:**
```typescript
allPayments: this.paymentService.getAll(id).pipe(catchError(() => of({ results: [] }))),
```

**In forkJoin next callback:**
```typescript
this.allPayments = allPayments?.results ?? [];
this.hasPaymentObjection = filing?.has_payment_objection === true;
this.paymentObjectionAmount = filing?.payment_objection_amount ?? null;
this.objectionResolvedByPayment = filing?.objection_resolved_by_payment ?? null;
```

---

## ADVOCATE - View & Resolve Payment Objection

### TypeScript (scrutiny-details.ts)

**Variables (add to class):**
```typescript
hasPaymentObjection = false;
paymentObjectionAmount: number | null = null;
isPayingNow = false;
allPayments: any[] = [];
resolvedObjections: any[] = [];
objectionResolvedByPayment: any | null = null;
collapsedPayments = new Set<number>();
```

**togglePaymentCollapse method:**
```typescript
togglePaymentCollapse(paymentId: number): void {
  if (this.collapsedPayments.has(paymentId)) {
    this.collapsedPayments.delete(paymentId);
  } else {
    this.collapsedPayments.add(paymentId);
  }
}
```

**isPaymentCollapsed method:**
```typescript
isPaymentCollapsed(paymentId: number): boolean {
  return !this.collapsedPayments.has(paymentId);
}
```

**sortedPayments getter:**
```typescript
get sortedPayments(): any[] {
  return [...this.allPayments].sort((a, b) => {
    const dateA = new Date(a.payment_datetime || 0).getTime();
    const dateB = new Date(b.payment_datetime || 0).getTime();
    return dateB - dateA;
  });
}
```

**getPaymentStatusLabel method:**
```typescript
getPaymentStatusLabel(status: string | null): string {
  if (!status) return 'Unknown';
  const s = status.toLowerCase();
  if (/(success|paid|complete|ok)/i.test(s)) return 'Success';
  if (/failed/i.test(s)) return 'Failed';
  if (/pending|initiated/i.test(s)) return 'Pending';
  if (/offline_submitted|submitted/i.test(s)) return 'Submitted';
  return status;
}
```

**getPaymentStatusClass method:**
```typescript
getPaymentStatusClass(status: string | null): string {
  const label = this.getPaymentStatusLabel(status).toLowerCase();
  if (label.includes('success')) return 'text-success';
  if (label.includes('fail')) return 'text-danger';
  if (label.includes('pending')) return 'text-warning';
  return 'text-muted';
}
```

**payNow() method:**
```typescript
payNow(): void {
  if (!this.filingId || !this.paymentObjectionAmount) {
    this.toastr.error("Unable to initiate payment. Please try again.");
    return;
  }

  this.router.navigate(["/advocate/dashboard/efiling/payment-confirmation"], {
    queryParams: { id: this.filingId },
  });
}
```

**resubmitForScrutiny() method:**
```typescript
resubmitForScrutiny(): void {
  if (!this.filingId) return;
  const filingId = this.filingId;

  Swal.fire({
    title: "Resubmit for Scrutiny?",
    text: "Your case will be resubmitted after resolving the payment objection. It will be forwarded for scrutiny.",
    icon: "question",
    showCancelButton: true,
    confirmButtonText: "Resubmit",
    cancelButtonText: "Cancel",
  }).then((result) => {
    if (result.isConfirmed) {
      this.efilingService.resubmit_after_payment_objection(filingId).subscribe({
        next: (response) => {
          this.toastr.success("Your case has been resubmitted for scrutiny.");
          sessionStorage.removeItem("paymentResubmission_" + filingId);
          this.loadDetails(filingId);
        },
        error: (error) => {
          this.toastr.error(
            error?.error?.message || "Failed to resubmit for scrutiny."
          );
        },
      });
    }
  });
}
```

**In loadDetails() forkJoin:**
```typescript
allPayments: this.paymentService.getAll(id).pipe(catchError(() => of({ results: [] }))),
```

**In forkJoin next callback:**
```typescript
this.allPayments = allPayments?.results ?? [];
this.hasPaymentObjection = filing?.has_payment_objection === true;
this.paymentObjectionAmount = filing?.payment_objection_amount ?? null;
this.objectionResolvedByPayment = filing?.objection_resolved_by_payment ?? null;
```

---

## SERVICE METHODS (efiling.services.ts)

**raise_payment_objection:**
```typescript
raise_payment_objection(id: number, courtFeeAmount: number): Observable<any> {
  return this.http.post<any>(
    `${app_url}/api/v1/efiling/payment-objections/`,
    { e_filing: id, court_fee_amount: courtFeeAmount },
  );
}
```

**reset_payment_objection:**
```typescript
reset_payment_objection(id: number): Observable<any> {
  return this.http.post<any>(
    `${app_url}/api/v1/efiling/payment-objections/reset/`,
    { e_filing: id },
  );
}
```

**resubmit_after_payment_objection:**
```typescript
resubmit_after_payment_objection(id: number): Observable<any> {
  return this.http.post<any>(
    `${app_url}/api/v1/efiling/payment-objections/resubmit/`,
    { e_filing: id },
  );
}
```

---

## HTML TEMPLATE - Scrutiny Officer (details.html)

**Add inside Filing Summary section under Payment Details:**

```html
<!-- Payment Details Section -->
<div class="filing-summary-section">
  <div class="filing-summary-section-title">
    <i class="fa-solid fa-indian-rupee-sign me-2"></i>
    Payment Details
  </div>

  <!-- All Payments - Collapsible -->
  <div *ngIf="sortedPayments.length > 0" class="payments-list mb-3">
    <div class="payment-card border rounded mb-2" *ngFor="let payment of sortedPayments">
      <div
        class="payment-card-header d-flex justify-content-between align-items-center p-2 cursor-pointer bg-light"
        (click)="togglePaymentCollapse(payment.id)"
      >
        <div class="d-flex align-items-center gap-2">
          <i class="fa-solid" [ngClass]="isPaymentCollapsed(payment.id) ? 'fa-chevron-down' : 'fa-chevron-up'"></i>
          <span class="fw-semibold">Payment</span>
          <span class="badge" [ngClass]="getPaymentStatusLabel(payment.status) === 'Success' ? 'bg-success' : 'bg-secondary'">
            {{ getPaymentStatusLabel(payment.status) }}
          </span>
        </div>
        <div class="d-flex align-items-center gap-3">
          <span class="fw-semibold">₹{{ payment.amount || '-' }}/-</span>
          <span class="small text-muted">{{ payment.payment_datetime | date: 'dd MMM yyyy' }}</span>
        </div>
      </div>
      <div class="payment-card-body p-3" *ngIf="!isPaymentCollapsed(payment.id)">
        <div class="row g-3">
          <div class="col-md-6">
            <div class="text-muted small">Payment Status</div>
            <div [ngClass]="getPaymentStatusClass(payment.status)">
              <i class="fa-solid me-1" [ngClass]="getPaymentStatusLabel(payment.status) === 'Success' ? 'fa-check-circle' : 'fa-clock'"></i>
              {{ getPaymentStatusLabel(payment.status) }}
            </div>
          </div>
          <div class="col-md-6">
            <div class="text-muted small">Payment Mode</div>
            <div class="text-capitalize">{{ payment.payment_mode || '-' }}</div>
          </div>
          <div class="col-md-6">
            <div class="text-muted small">Transaction ID</div>
            <div>{{ payment.txn_id || '-' }}</div>
          </div>
          <div class="col-md-6">
            <div class="text-muted small">Reference ID</div>
            <div>{{ payment.reference_no || '-' }}</div>
          </div>
          <div class="col-md-6">
            <div class="text-muted small">Amount</div>
            <div class="fw-semibold">₹{{ payment.amount || '-' }}/-</div>
          </div>
          <div class="col-md-6">
            <div class="text-muted small">Date & Time</div>
            <div>{{ payment.payment_datetime | date: 'dd MMM yyyy, hh:mm a' }}</div>
          </div>
          <div class="col-md-6" *ngIf="payment.bank_receipt">
            <div class="text-muted small">Bank Receipt</div>
            <div>
              <a [href]="payment.bank_receipt" target="_blank" class="btn btn-sm btn-outline-primary">
                <i class="fa-solid fa-file-pdf me-1"></i>View Receipt
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Empty Payment State -->
  <div *ngIf="sortedPayments.length === 0" class="text-muted small mb-3">
    No payments recorded yet.
  </div>

  <!-- Raise Objection on Payment -->
  <div class="payment-objection-section mt-3 p-3 border rounded bg-light">
    <div class="d-flex align-items-center justify-content-between mb-2">
      <div class="form-check">
        <input
          class="form-check-input"
          type="checkbox"
          id="raisePaymentObjection"
          [(ngModel)]="raisePaymentObjection"
          [ngModelOptions]="{ standalone: true }"
        />
        <label class="form-check-label fw-semibold text-danger" for="raisePaymentObjection">
          <i class="fa-solid fa-triangle-exclamation me-1"></i>
          Raise Objection on Payment
        </label>
      </div>
      <div class="d-flex align-items-center gap-2">
        <span class="badge bg-secondary" *ngIf="hasPaymentObjection && !isPaymentObjectionResolved">
          <i class="fa-solid fa-clock me-1"></i>Pending
        </span>
        <span class="badge bg-success" *ngIf="isPaymentObjectionResolved">
          <i class="fa-solid fa-check me-1"></i>Resolved
        </span>
        <span class="badge bg-danger" *ngIf="raisePaymentObjection">Active</span>
      </div>
    </div>

    <!-- Existing Objection Alert -->
    <div class="alert alert-danger py-2 small mb-0" *ngIf="hasPaymentObjection && !isPaymentObjectionResolved">
      <div class="d-flex align-items-start">
        <i class="fa-solid fa-exclamation-circle me-2 mt-1"></i>
        <div>
          <strong>Payment Objection Active</strong>
          <div class="mt-1">An objection was raised for court fee amount of <strong>₹{{ paymentObjectionAmount }}/-</strong>.</div>
          <div class="small text-muted mt-1">Awaiting advocate to make correct payment.</div>
        </div>
      </div>
    </div>

    <!-- Resolved Objection Alert -->
    <div class="alert alert-success py-2 small mb-3" *ngIf="isPaymentObjectionResolved && objectionResolvedByPayment">
      <div class="d-flex align-items-start">
        <i class="fa-solid fa-check-circle me-2 mt-1"></i>
        <div>
          <strong>Payment Objection Resolved</strong>
          <div class="mt-1">Payment of <strong>₹{{ objectionResolvedByPayment.amount }}/-</strong> (Txn: {{ objectionResolvedByPayment.txn_id }}) matches the required court fee.</div>
        </div>
      </div>
    </div>

    <div class="payment-objection-form mt-3" *ngIf="raisePaymentObjection">
      <div class="alert alert-warning py-2 small mb-3">
        <i class="fa-solid fa-circle-info me-1"></i>
        The advocate will be notified of the objection and asked to pay the correct court fee amount.
      </div>
      <div class="row g-3 align-items-end">
        <div class="col-md-5">
          <label class="form-label small fw-semibold" for="directCourtFeeAmount">
            Direct Court Fee Amount (INR)
          </label>
          <div class="input-group input-group-sm">
            <span class="input-group-text">₹</span>
            <input
              id="directCourtFeeAmount"
              type="number"
              class="form-control"
              [(ngModel)]="directCourtFeeAmount"
              [ngModelOptions]="{ standalone: true }"
              placeholder="e.g. 500"
              min="0.01"
              step="0.01"
            />
          </div>
        </div>
        <div class="col-md-4">
          <button
            type="button"
            class="btn btn-danger w-100"
            [disabled]="!canSubmitPaymentObjection"
            (click)="submitPaymentObjection()"
          >
            <span
              *ngIf="isSubmittingPaymentObjection"
              class="spinner-border spinner-border-sm me-1"
              role="status"
            ></span>
            <i *ngIf="!isSubmittingPaymentObjection" class="fa-solid fa-paper-plane me-1"></i>
            {{ isSubmittingPaymentObjection ? 'Submitting...' : 'Submit Objection' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</div>
```

---

## BACKEND API ENDPOINTS (Django)

### URLs (efiling/urls.py)
```python
path(
    "payment-objections/",
    PaymentObjectionViewSet.as_view({'get': 'list', 'post': 'create'}),
    name="payment-objection-list-create",
),
path(
    "payment-objections/resubmit/",
    PaymentObjectionViewSet.as_view({'post': 'resubmit'}),
    name="payment-objection-resubmit",
),
```

### Views (efiling/views/payment_objection_views.py)

```python
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from apps.core.models import Efiling
from apps.efiling.models import PaymentObjection, EfilingNotification


class PaymentObjectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentObjection
        fields = [
            'id',
            'e_filing',
            'court_fee_amount',
            'status',
            'remarks',
            'raised_by',
            'raised_at',
            'resolved_at',
            'resolved_by_payment_id',
        ]
        read_only_fields = ['id', 'raised_by', 'raised_at', 'resolved_at', 'resolved_by_payment_id']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['raised_by'] = request.user
        return super().create(validated_data)


class PaymentObjectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payment objections on e-filings.
    When a payment objection is created, the associated e-filing status
    is updated to reflect the rejection due to payment objection.
    """
    queryset = PaymentObjection.objects.all()
    serializer_class = PaymentObjectionSerializer
    http_method_names = ['post', 'get', 'head', 'options']

    def perform_create(self, serializer):
        """Save the payment objection and update e-filing status."""
        objection = serializer.save()

        # Update e-filing status to reflect payment objection rejection
        if objection.e_filing:
            objection.e_filing.status = 'REJECTED_PAYMENT_OBJECTION'
            objection.e_filing.save(update_fields=['status', 'updated_at'])

    def create(self, request, *args, **kwargs):
        """Create a new payment objection."""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['post'])
    def reset(self, request):
        """
        Reset/cancel a pending payment objection for an e-filing.
        This endpoint is called by the scrutiny officer to cancel an objection
        if it was raised in error.
        
        Expected payload: { "e_filing": <id> }
        """
        e_filing_id = request.data.get('e_filing')
        if not e_filing_id:
            return Response(
                {'error': 'e_filing id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            e_filing = Efiling.objects.get(pk=e_filing_id)
        except Efiling.DoesNotExist:
            return Response(
                {'error': 'E-filing not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        pending_objection = PaymentObjection.objects.filter(
            e_filing=e_filing,
            status=PaymentObjection.Status.PENDING
        ).first()

        if not pending_objection:
            return Response(
                {'error': 'No pending payment objection found for this filing'},
                status=status.HTTP_400_BAD_REQUEST
            )

        pending_objection.delete()

        e_filing.status = 'UNDER_SCRUTINY'
        e_filing.save(update_fields=['status', 'updated_at'])

        return Response({
            'message': 'Payment objection reset successfully',
            'e_filing_id': e_filing.id,
            'status': e_filing.status,
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def resubmit(self, request):
        """
        Handle resubmission of an e-filing after payment objection.
        This endpoint is called when an advocate resubmits their case
        after paying the correct court fee.
        
        Expected payload: { "e_filing": <id>, "payment_id": <optional_payment_id> }
        """
        e_filing_id = request.data.get('e_filing')
        payment_id = request.data.get('payment_id')
        if not e_filing_id:
            return Response(
                {'error': 'e_filing id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            e_filing = Efiling.objects.get(pk=e_filing_id)
        except Efiling.DoesNotExist:
            return Response(
                {'error': 'E-filing not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if there's a pending payment objection
        pending_objection = PaymentObjection.objects.filter(
            e_filing=e_filing,
            status=PaymentObjection.Status.PENDING
        ).first()

        if not pending_objection:
            return Response(
                {'error': 'No pending payment objection found for this filing'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Resolve the payment objection
        pending_objection.status = PaymentObjection.Status.RESOLVED
        pending_objection.resolved_at = timezone.now()
        if payment_id:
            pending_objection.resolved_by_payment_id = str(payment_id)
        pending_objection.save(update_fields=['status', 'resolved_at', 'resolved_by_payment_id'])

        # Update e-filing status to resubmitted (under scrutiny)
        e_filing.status = 'UNDER_SCRUTINY'
        e_filing.save(update_fields=['status', 'updated_at'])

        # Create notification for scrutiny officer
        EfilingNotification.objects.create(
            role=EfilingNotification.Role.SCRUTINY_OFFICER,
            notification_type=EfilingNotification.NotificationType.FILING_SUBMITTED,
            message=f"Case {e_filing.e_filing_number} has been resubmitted after resolving payment objection. Please review.",
            e_filing=e_filing,
            link_url=f"/scrutiny-officers/dashboard/filed-cases/details/{e_filing.id}",
        )

        # Create notification for advocate (confirmation)
        EfilingNotification.objects.create(
            role=EfilingNotification.Role.ADVOCATE,
            notification_type=EfilingNotification.NotificationType.FILING_SUBMITTED,
            message=f"Your case {e_filing.e_filing_number} has been resubmitted for scrutiny after resolving the payment objection.",
            e_filing=e_filing,
        )

        return Response({
            'message': 'Filing resubmitted successfully',
            'e_filing_id': e_filing.id,
            'status': e_filing.status,
        }, status=status.HTTP_200_OK)
```

### Model (efiling/models.py - PaymentObjection)

```python
class PaymentObjection(models.Model):
    """
    Tracks payment objections raised by scrutiny officer against an e-filing.
    When a scrutiny officer raises a payment objection, this record is created
    and the e-filing status is updated to reflect the objection.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        RESOLVED = "RESOLVED", "Resolved"
        CANCELLED = "CANCELLED", "Cancelled"

    e_filing = models.ForeignKey(
        Efiling,
        on_delete=models.CASCADE,
        related_name="payment_objections"
    )
    court_fee_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="The correct court fee amount as determined by the scrutiny officer"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    remarks = models.TextField(
        blank=True,
        null=True,
        help_text="Optional remarks explaining the payment objection"
    )
    raised_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="raised_payment_objections",
        help_text="The scrutiny officer who raised the objection"
    )
    raised_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp when the objection was resolved"
    )
    resolved_by_payment_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="The payment transaction ID that resolved this objection"
    )

    class Meta:
        db_table = "efiling_payment_objection"
        ordering = ["-raised_at"]
```

---

## PAYMENT CONFIRMATION COMPONENT (Advocate)

This component loads when advocate clicks "Pay Now" from scrutiny-details. It allows:
1. View active payment objection details
2. Pay online via payment gateway OR submit offline bank receipt
3. After successful payment, "Resubmit for Scrutiny" button appears

### TypeScript (payment-confirmation/payment-confirmation.ts)

```typescript
import { CommonModule } from "@angular/common";
import { Component, OnInit } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { ActivatedRoute, Router, RouterLink } from "@angular/router";
import { firstValueFrom } from "rxjs";
import Swal from "sweetalert2";
import { ToastrService } from "ngx-toastr";
import { EfilingService } from "../../../../../services/advocate/efiling/efiling.services";
import { PaymentService } from "../../../../../services/payment/payment.service";

@Component({
  selector: "app-payment-confirmation",
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  templateUrl: "./payment-confirmation.html",
  styleUrls: ["./payment-confirmation.css"],
})
export class PaymentConfirmation implements OnInit {
  filingId: number | null = null;
  filing: any = null;
  paymentOutcome: "success" | "failed" | null = null;
  paymentDetails: any = null;
  isLoading = true;
  isResolving = false;
  objectionResolvedByPayment: any | null = null;
  hasPaymentObjection = false;
  paymentObjectionAmount: number | null = null;

  paymentMode: "online" | "offline" = "online";
  offlineTransactionId = "";
  offlinePaymentDate = "";
  offlineBankReceipt: File | null = null;
  offlineBankReceiptName = "";
  isSubmittingOfflinePayment = false;
  isPayingOnline = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private efilingService: EfilingService,
    private paymentService: PaymentService,
    private toastr: ToastrService,
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe(async (params) => {
      this.filingId = Number(params["id"] || params["application"] || 0) || null;
      this.paymentOutcome = null;
      this.paymentDetails = null;
      this.resetPaymentForm();

      // Handle payment gateway return status (success/failed)
      const statusRaw = params["status"] ?? params["payment_status"] ?? params["txn_status"];
      if (statusRaw !== undefined && statusRaw !== null && statusRaw !== "") {
        const st = String(statusRaw).trim().toLowerCase();
        if (/(success|paid|complete|ok)/i.test(st)) {
          this.paymentOutcome = "success";
        } else if (/(fail|reject|declin|error|cancel)/i.test(st)) {
          this.paymentOutcome = "failed";
        }
      }

      if (this.filingId) {
        await this.loadFilingDetails();
      }
      this.isLoading = false;
    });
  }

  private resetPaymentForm(): void {
    this.paymentMode = "online";
    this.offlineTransactionId = "";
    this.offlinePaymentDate = "";
    this.offlineBankReceipt = null;
    this.offlineBankReceiptName = "";
  }

  private async loadFilingDetails(): Promise<void> {
    if (!this.filingId) return;

    try {
      const filing = await firstValueFrom(
        this.efilingService.get_filing_by_id(this.filingId)
      );
      this.filing = filing;
      this.objectionResolvedByPayment = filing?.objection_resolved_by_payment ?? null;
      this.hasPaymentObjection = filing?.has_payment_objection === true;
      this.paymentObjectionAmount = filing?.payment_objection_amount ?? null;

      // If objection is resolved or no active objection, load payment details to show status
      if (!this.hasPaymentObjection) {
        await this.loadPaymentDetailsFromBackend();
      }
    } catch (error) {
      console.error("Failed to load filing details", error);
      this.toastr.error("Failed to load filing details");
    }
  }

  private async loadPaymentDetailsFromBackend(): Promise<void> {
    if (!this.filingId) return;
    try {
      const tx = await firstValueFrom(this.paymentService.latest(this.filingId));
      if (tx && (tx.txn_id || tx.reference_no || tx.status)) {
        const statusRaw = String(tx.status || "").toLowerCase();
        const paymentMode =
          String(tx.payment_mode || "").toLowerCase() === "offline" ? "offline" : "online";
        if (
          /(success|paid|complete|ok)/i.test(statusRaw) ||
          (paymentMode === "offline" && !!tx.bank_receipt)
        ) {
          this.paymentOutcome = "success";
        } else if (statusRaw) {
          this.paymentOutcome = "failed";
        }
        this.paymentDetails = {
          txnId: tx.txn_id || undefined,
          paidAt: tx.payment_datetime || tx.paid_at || undefined,
          referenceNo: tx.reference_no || undefined,
          amount: tx.amount || undefined,
          courtFees: tx.court_fees || tx.amount || undefined,
          paymentMode,
          bankReceipt: tx.bank_receipt || undefined,
          paymentDate: tx.payment_date || undefined,
        };
      }
    } catch (error) {
      console.error("Failed to load payment details", error);
    }
  }

  get isObjectionResolved(): boolean {
    return this.objectionResolvedByPayment !== null && this.hasPaymentObjection === false;
  }

  get showPaymentForm(): boolean {
    return this.hasPaymentObjection && !this.isObjectionResolved && this.paymentOutcome !== 'failed';
  }

  get canSubmitOffline(): boolean {
    return (
      !!this.offlineTransactionId.trim() &&
      !!this.offlinePaymentDate &&
      !!this.offlineBankReceipt &&
      this.paymentObjectionAmount !== null &&
      this.paymentObjectionAmount > 0 &&
      !this.isSubmittingOfflinePayment
    );
  }

  onPaymentModeChange(mode: "online" | "offline"): void {
    this.paymentMode = mode;
  }

  onOfflineReceiptChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      if (file.size > 10 * 1024 * 1024) {
        this.toastr.error("File size must be less than 10MB");
        return;
      }
      this.offlineBankReceipt = file;
      this.offlineBankReceiptName = file.name;
    }
  }

  async proceedToPayOnline(): Promise<void> {
    if (!this.filingId || !this.paymentObjectionAmount || this.paymentObjectionAmount <= 0) {
      this.toastr.error("Invalid payment amount");
      return;
    }

    const result = await Swal.fire({
      title: "Proceed to pay court fee?",
      html: `You will be redirected to the payment gateway to pay <strong>₹${this.paymentObjectionAmount}</strong> for this filing.`,
      icon: "question",
      showCancelButton: true,
      confirmButtonText: "Yes, proceed to pay",
      cancelButtonText: "Cancel",
    });
    if (!result.isConfirmed) return;

    this.isPayingOnline = true;
    try {
      const init = await firstValueFrom(
        this.paymentService.initiate({
          amount: this.paymentObjectionAmount,
          application: this.filingId,
          e_filing_number: this.filing?.e_filing_number || "",
          payment_type: "application",
          source: "objection",
        })
      );
      this.postToGateway(init.action, init.fields as Record<string, string>);
    } catch (e) {
      console.error(e);
      this.isPayingOnline = false;
      this.toastr.error("Could not start payment. Please try again.");
    }
  }

  private postToGateway(action: string, fields: Record<string, string>): void {
    const form = document.createElement("form");
    form.method = "POST";
    form.action = action;
    form.style.display = "none";
    form.acceptCharset = "UTF-8";
    for (const [key, value] of Object.entries(fields)) {
      const inp = document.createElement("input");
      inp.type = "hidden";
      inp.name = key;
      inp.value = value == null ? "" : String(value);
      form.appendChild(inp);
    }
    document.body.appendChild(form);
    form.submit();
  }

  async submitOfflinePayment(): Promise<void> {
    if (!this.canSubmitOffline || !this.filingId) return;

    this.isSubmittingOfflinePayment = true;
    try {
      await firstValueFrom(
        this.paymentService.submitOffline({
          application: this.filingId,
          txn_id: this.offlineTransactionId.trim(),
          court_fees: this.paymentObjectionAmount!,
          payment_date: this.offlinePaymentDate,
          payment_type: "Court Fees",
          e_filing_number: this.filing?.e_filing_number || "",
          bank_receipt: this.offlineBankReceipt!,
        })
      );

      this.toastr.success("Offline payment submitted successfully!");
      await this.loadFilingDetails();
      this.resetPaymentForm();
    } catch (error: any) {
      console.error("Failed to submit offline payment", error);
      this.toastr.error(error?.error?.detail || "Failed to submit offline payment");
    } finally {
      this.isSubmittingOfflinePayment = false;
    }
  }

  async resubmitForScrutiny(): Promise<void> {
    if (!this.filingId || !this.isObjectionResolved) {
      this.toastr.error("Objection is not resolved. Please make the correct payment first.");
      return;
    }

    const result = await Swal.fire({
      title: "Resubmit for Scrutiny?",
      html: "Your filing will be resubmitted for scrutiny. The scrutiny officer will review your corrected payment.",
      icon: "question",
      showCancelButton: true,
      confirmButtonText: "Yes, Resubmit",
      cancelButtonText: "Cancel",
      confirmButtonColor: "#198754",
      cancelButtonColor: "#6c757d",
    });

    if (!result.isConfirmed) return;

    this.isResolving = true;
    try {
      const response = await firstValueFrom(
        this.efilingService.resubmit_after_payment_objection(this.filingId)
      );
      this.toastr.success("Filing resubmitted for scrutiny successfully!");
      this.router.navigate(["/advocate/dashboard/efiling/pending-scrutiny"]);
    } catch (error: any) {
      console.error("Failed to resubmit", error);
      this.toastr.error(error?.error?.error || error?.message || "Failed to resubmit filing.");
    } finally {
      this.isResolving = false;
    }
  }

  goToPendingScrutiny(): void {
    this.router.navigate(["/advocate/dashboard/efiling/pending-scrutiny"]);
  }

  formatDateTime(dateStr: string | undefined): string {
    if (!dateStr) return "-";
    const d = new Date(dateStr);
    if (!Number.isNaN(d.getTime())) return d.toLocaleString();
    return String(dateStr);
  }
}
```

### HTML (payment-confirmation/payment-confirmation.html)

```html
<div class="payment-confirmation-page">
  <div class="container py-4">
    <!-- Loading State -->
    <div *ngIf="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="mt-3 text-muted">Loading payment details...</p>
    </div>

    <!-- Content -->
    <div *ngIf="!isLoading" class="row justify-content-center">
      <div class="col-md-8 col-lg-6">
        
        <!-- Success Card -->
        <div *ngIf="paymentOutcome === 'success'" class="card border-success shadow-sm mb-4">
          <div class="card-header bg-success text-white py-3">
            <h5 class="mb-0">
              <i class="fa-solid fa-check-circle me-2"></i>
              Payment Successful
            </h5>
          </div>
          <div class="card-body">
            
            <!-- Objection Resolved Alert -->
            <div *ngIf="isObjectionResolved" class="alert alert-success py-2 mb-4">
              <i class="fa-solid fa-check-circle me-2"></i>
              <strong>Payment Objection Resolved!</strong>
              <p class="mb-0 small mt-1">
                Your payment of ₹{{ objectionResolvedByPayment?.amount }} has resolved the objection.
                Transaction ID: {{ objectionResolvedByPayment?.txn_id || '-' }}
              </p>
            </div>

            <!-- Payment Details -->
            <div *ngIf="paymentDetails" class="payment-details mb-4">
              <h6 class="text-muted mb-3">Payment Details</h6>
              <div class="row g-3">
                <div class="col-6">
                  <div class="text-muted small">Transaction ID</div>
                  <div class="fw-semibold">{{ paymentDetails.txnId || '-' }}</div>
                </div>
                <div class="col-6">
                  <div class="text-muted small">Reference Number</div>
                  <div class="fw-semibold">{{ paymentDetails.referenceNo || '-' }}</div>
                </div>
                <div class="col-6">
                  <div class="text-muted small">Amount Paid</div>
                  <div class="fw-semibold text-success">₹{{ paymentDetails.amount || paymentDetails.courtFees || '-' }}/-</div>
                </div>
                <div class="col-6">
                  <div class="text-muted small">Payment Mode</div>
                  <div class="fw-semibold text-capitalize">{{ paymentDetails.paymentMode || 'Online' }}</div>
                </div>
                <div class="col-6">
                  <div class="text-muted small">Date & Time</div>
                  <div class="fw-semibold">{{ formatDateTime(paymentDetails.paidAt) }}</div>
                </div>
                <div class="col-6" *ngIf="paymentDetails.bankReceipt">
                  <div class="text-muted small">Bank Receipt</div>
                  <div>
                    <a [href]="paymentDetails.bankReceipt" target="_blank" class="btn btn-sm btn-outline-primary">
                      <i class="fa-solid fa-file-pdf me-1"></i>View
                    </a>
                  </div>
                </div>
              </div>
            </div>

            <!-- Filing Info -->
            <div *ngIf="filing" class="filing-info mb-4">
              <h6 class="text-muted mb-3">Filing Information</h6>
              <div class="row g-3">
                <div class="col-12">
                  <div class="text-muted small">E-Filing Number</div>
                  <div class="fw-semibold filing-number">{{ filing.e_filing_number || '-' }}</div>
                </div>
                <div class="col-6">
                  <div class="text-muted small">Case Type</div>
                  <div class="fw-semibold">{{ filing.case_type?.type_name || filing.case_type?.full_form || '-' }}</div>
                </div>
                <div class="col-6">
                  <div class="text-muted small">Filing Status</div>
                  <div class="fw-semibold">{{ filing.status || '-' }}</div>
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="d-grid gap-2 mt-4">
              <button
                *ngIf="isObjectionResolved"
                type="button"
                class="btn btn-success btn-lg"
                [disabled]="isResolving"
                (click)="resubmitForScrutiny()"
              >
                <span *ngIf="isResolving" class="spinner-border spinner-border-sm me-2" role="status"></span>
                {{ isResolving ? 'Resubmitting...' : 'Resubmit for Scrutiny' }}
              </button>
              
              <button
                type="button"
                class="btn btn-outline-primary"
                (click)="goToPendingScrutiny()"
              >
                Go to Pending Scrutiny
              </button>
            </div>
          </div>
        </div>

        <!-- Failed Card -->
        <div *ngIf="paymentOutcome === 'failed' && !showPaymentForm" class="card border-danger shadow-sm mb-4">
          <div class="card-header bg-danger text-white py-3">
            <h5 class="mb-0">
              <i class="fa-solid fa-times-circle me-2"></i>
              Payment Failed
            </h5>
          </div>
          <div class="card-body">
            <div class="alert alert-danger py-2 mb-4">
              <i class="fa-solid fa-exclamation-circle me-2"></i>
              Your payment could not be processed. Please try again.
            </div>

            <div *ngIf="hasPaymentObjection && paymentObjectionAmount" class="alert alert-warning py-2 mb-4">
              <strong>Payment Objection Active:</strong>
              Please pay the correct court fee amount of ₹{{ paymentObjectionAmount }}/- as specified by the scrutiny officer.
            </div>

            <div class="d-grid gap-2 mt-4">
              <button
                type="button"
                class="btn btn-outline-secondary"
                (click)="goToPendingScrutiny()"
              >
                Go to Pending Scrutiny
              </button>
            </div>
          </div>
        </div>

        <!-- Neutral/No Payment State -->
        <div *ngIf="(!paymentOutcome || paymentOutcome === null) && !showPaymentForm" class="card border-secondary shadow-sm mb-4">
          <div class="card-header bg-secondary text-white py-3">
            <h5 class="mb-0">
              <i class="fa-solid fa-info-circle me-2"></i>
              Payment Status Unknown
            </h5>
          </div>
          <div class="card-body">
            <p class="text-muted">Unable to determine payment status.</p>
            
            <div *ngIf="filing" class="filing-info mb-4">
              <h6 class="text-muted mb-3">Filing Information</h6>
              <div class="row g-3">
                <div class="col-12">
                  <div class="text-muted small">E-Filing Number</div>
                  <div class="fw-semibold filing-number">{{ filing.e_filing_number || '-' }}</div>
                </div>
                <div class="col-6">
                  <div class="text-muted small">Case Type</div>
                  <div class="fw-semibold">{{ filing.case_type?.type_name || '-' }}</div>
                </div>
                <div class="col-6">
                  <div class="text-muted small">Filing Status</div>
                  <div class="fw-semibold">{{ filing.status || '-' }}</div>
                </div>
              </div>
            </div>

            <div class="d-grid gap-2 mt-4">
              <a
                [routerLink]="['/advocate/dashboard/efiling/draft-filings/edit']"
                [queryParams]="{ id: filingId }"
                class="btn btn-primary"
              >
                <i class="fa-solid fa-edit me-2"></i>
                Go to Draft Filing
              </a>
              
              <button
                type="button"
                class="btn btn-outline-secondary"
                (click)="goToPendingScrutiny()"
              >
                Go to Pending Scrutiny
              </button>
            </div>
          </div>
        </div>

        <!-- Payment Objection Active - Make Payment Section -->
        <div *ngIf="showPaymentForm" class="card border-warning shadow-sm mb-4">
          <div class="card-header bg-warning text-dark py-3">
            <h5 class="mb-0">
              <i class="fa-solid fa-exclamation-triangle me-2"></i>
              Payment Objection Active
            </h5>
          </div>
          <div class="card-body">
            <div class="alert alert-warning py-2 mb-4">
              <strong>Attention Required</strong>
              <p class="mb-0 mt-1">
                The scrutiny officer has raised a payment objection. Please pay the correct court fee amount of 
                <strong class="fs-5">₹{{ paymentObjectionAmount }}/-</strong> to resolve this objection.
              </p>
            </div>

            <!-- Filing Info -->
            <div *ngIf="filing" class="filing-info mb-4">
              <div class="row g-3">
                <div class="col-12">
                  <div class="text-muted small">E-Filing Number</div>
                  <div class="fw-semibold filing-number">{{ filing.e_filing_number || '-' }}</div>
                </div>
                <div class="col-6">
                  <div class="text-muted small">Case Type</div>
                  <div class="fw-semibold">{{ filing.case_type?.type_name || '-' }}</div>
                </div>
                <div class="col-6">
                  <div class="text-muted small">Filing Status</div>
                  <div class="fw-semibold">{{ filing.status || '-' }}</div>
                </div>
              </div>
            </div>

            <!-- Payment Mode Selection -->
            <div class="mb-4">
              <label class="form-label fw-semibold">Select Payment Mode</label>
              <div class="d-flex gap-3">
                <div class="form-check">
                  <input
                    class="form-check-input"
                    type="radio"
                    name="paymentMode"
                    id="paymentModeOnline"
                    [checked]="paymentMode === 'online'"
                    (change)="onPaymentModeChange('online')"
                  />
                  <label class="form-check-label" for="paymentModeOnline">
                    <i class="fa-solid fa-credit-card me-1"></i> Online Payment
                  </label>
                </div>
                <div class="form-check">
                  <input
                    class="form-check-input"
                    type="radio"
                    name="paymentMode"
                    id="paymentModeOffline"
                    [checked]="paymentMode === 'offline'"
                    (change)="onPaymentModeChange('offline')"
                  />
                  <label class="form-check-label" for="paymentModeOffline">
                    <i class="fa-solid fa-building-columns me-1"></i> Offline (Bank Receipt)
                  </label>
                </div>
              </div>
            </div>

            <!-- Online Payment -->
            <div *ngIf="paymentMode === 'online'" class="card border bg-light mb-3">
              <div class="card-body py-3">
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <span class="text-muted">Amount payable</span>
                  <span class="fs-5 fw-semibold text-success">₹{{ paymentObjectionAmount }}/-</span>
                </div>
                <button
                  type="button"
                  class="btn btn-primary w-100"
                  [disabled]="isPayingOnline || !paymentObjectionAmount"
                  (click)="proceedToPayOnline()"
                >
                  <span *ngIf="isPayingOnline" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  <i class="fa-solid fa-arrow-up-right-from-square me-2"></i>
                  {{ isPayingOnline ? 'Redirecting...' : 'Pay via Payment Gateway' }}
                </button>
              </div>
            </div>

            <!-- Offline Payment -->
            <div *ngIf="paymentMode === 'offline'" class="card border bg-light mb-3">
              <div class="card-body py-3">
                <h6 class="text-muted mb-3">Submit Bank Receipt</h6>
                <div class="row g-3">
                  <div class="col-md-4">
                    <label class="form-label mb-1 small">Bank Receipt No.</label>
                    <input
                      type="text"
                      class="form-control"
                      [(ngModel)]="offlineTransactionId"
                      [ngModelOptions]="{ standalone: true }"
                      placeholder="Enter Bank Receipt No."
                    />
                  </div>
                  <div class="col-md-4">
                    <label class="form-label mb-1 small">Date of Payment</label>
                    <input
                      type="date"
                      class="form-control"
                      [(ngModel)]="offlinePaymentDate"
                      [ngModelOptions]="{ standalone: true }"
                    />
                  </div>
                  <div class="col-md-4">
                    <label class="form-label mb-1 small">Upload Bank Receipt (PDF)</label>
                    <input
                      type="file"
                      class="form-control"
                      accept="application/pdf"
                      (change)="onOfflineReceiptChange($event)"
                    />
                    <div class="small text-muted mt-1" *ngIf="offlineBankReceiptName">
                      <i class="fa-solid fa-file-pdf me-1"></i>{{ offlineBankReceiptName }}
                    </div>
                  </div>
                </div>
                <div class="mt-3">
                  <button
                    type="button"
                    class="btn btn-primary"
                    [disabled]="!canSubmitOffline"
                    (click)="submitOfflinePayment()"
                  >
                    <span *ngIf="isSubmittingOfflinePayment" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    <i class="fa-solid fa-upload me-2"></i>
                    {{ isSubmittingOfflinePayment ? 'Submitting...' : 'Submit Offline Payment' }}
                  </button>
                </div>
              </div>
            </div>

            <div class="d-flex justify-content-between mt-4">
              <button
                type="button"
                class="btn btn-outline-secondary"
                (click)="goToPendingScrutiny()"
              >
                <i class="fa-solid fa-arrow-left me-2"></i>
                Go to Pending Scrutiny
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</div>
```

### CSS (payment-confirmation/payment-confirmation.css)

```css
.payment-confirmation-page {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.filing-number {
  font-family: monospace;
  letter-spacing: 0.5px;
}
```

### Route Configuration (app.routes.ts)

```typescript
{
  path: 'advocate/dashboard/efiling/payment-confirmation',
  loadComponent: () =>
    import(
      './areas/advocate/dashboard/efiling/payment-confirmation/payment-confirmation'
    ).then((m) => m.PaymentConfirmation),
},
```

### Navigation from scrutiny-details.ts

When advocate clicks "Pay Now" in scrutiny-details:

```typescript
payNow(): void {
  if (!this.filingId || !this.paymentObjectionAmount) {
    this.toastr.error("Unable to initiate payment. Please try again.");
    return;
  }

  this.router.navigate(["/advocate/dashboard/efiling/payment-confirmation"], {
    queryParams: { id: this.filingId },
  });
}
```

### Views (payment/views.py)

**raise_payment_objection:**
```python
@api_view(["POST"])
@permission_classes([ScrutinyOfficerPermission])
def raise_payment_objection(request):
    e_filing_id = request.data.get("e_filing")
    court_fee_amount = request.data.get("court_fee_amount")
    
    if not e_filing_id or not court_fee_amount:
        return Response(
            {"detail": "e_filing and court_fee_amount are required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        e_filing = Efiling.objects.get(id=e_filing_id)
    except Efiling.DoesNotExist:
        return Response(
            {"detail": "E-filing not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    payment_objection = PaymentObjection.objects.create(
        e_filing=e_filing,
        court_fee_amount=court_fee_amount,
        raised_by=request.user,
        status="pending"
    )
    
    # Update e-filing status
    e_filing.has_payment_objection = True
    e_filing.payment_objection_amount = court_fee_amount
    e_filing.status = "rejected_payment_objection"
    e_filing.save()
    
    # Notify advocate via chat/notification
    # ... (add notification logic)
    
    return Response(
        PaymentObjectionSerializer(payment_objection).data,
        status=status.HTTP_201_CREATED
    )
```

**reset_payment_objection:**
```python
@api_view(["POST"])
@permission_classes([ScrutinyOfficerPermission])
def reset_payment_objection(request):
    e_filing_id = request.data.get("e_filing")
    
    if not e_filing_id:
        return Response(
            {"detail": "e_filing is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        e_filing = Efiling.objects.get(id=e_filing_id)
        payment_objection = PaymentObjection.objects.filter(
            e_filing=e_filing,
            status="pending"
        ).first()
        
        if payment_objection:
            payment_objection.status = "reset"
            payment_objection.save()
        
        e_filing.has_payment_objection = False
        e_filing.payment_objection_amount = None
        e_filing.objection_resolved_by_payment = None
        e_filing.status = "under_scrutiny"
        e_filing.save()
        
        return Response(
            {"detail": "Payment objection reset successfully"},
            status=status.HTTP_200_OK
        )
    except Efiling.DoesNotExist:
        return Response(
            {"detail": "E-filing not found"},
            status=status.HTTP_404_NOT_FOUND
        )
```

**resubmit_after_payment_objection:**
```python
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def resubmit_after_payment_objection(request):
    e_filing_id = request.data.get("e_filing")
    
    if not e_filing_id:
        return Response(
            {"detail": "e_filing is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        e_filing = Efiling.objects.get(id=e_filing_id)
        
        # Verify payment matches required court fee
        required_amount = e_filing.payment_objection_amount
        latest_payment = Payment.objects.filter(
            e_filing=e_filing,
            status__in=["success", "paid", "complete"]
        ).order_by("-payment_datetime").first()
        
        if latest_payment and float(latest_payment.amount) >= float(required_amount):
            # Mark objection as resolved
            e_filing.objection_resolved_by_payment = {
                "amount": latest_payment.amount,
                "txn_id": latest_payment.txn_id,
                "resolved_at": str(latest_payment.payment_datetime)
            }
            e_filing.has_payment_objection = False
            e_filing.status = "under_scrutiny"
            e_filing.save()
            
            # Update payment objection status
            PaymentObjection.objects.filter(
                e_filing=e_filing,
                status="pending"
            ).update(status="resolved")
            
            return Response(
                {"detail": "Case resubmitted successfully after payment objection resolution"},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Payment amount does not match required court fee"},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Efiling.DoesNotExist:
        return Response(
            {"detail": "E-filing not found"},
            status=status.HTTP_404_NOT_FOUND
        )
```

### Model (PaymentObjection)
```python
class PaymentObjection(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("resolved", "Resolved"),
        ("reset", "Reset"),
    ]
    
    e_filing = models.ForeignKey(Efiling, on_delete=models.CASCADE, related_name="payment_objections")
    court_fee_amount = models.DecimalField(max_digits=10, decimal_places=2)
    raised_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "payment_objections"
```

---

## GOVERNMENT BODY - Skip Payment Feature

When "Filing as a Government Body" checkbox is checked, payment step is skipped entirely.

### initial-inputs Component (initial-inputs.ts)

```typescript
import { Component, EventEmitter, Input, Output } from "@angular/core";

@Component({
  selector: "app-initial-inputs",
  standalone: true,
  templateUrl: "./initial-inputs.html",
  styleUrl: "./initial-inputs.css",
})
export class InitialInputsComponent {
  @Input() isGovernmentBody = false;
  @Output() isGovernmentBodyChange = new EventEmitter<boolean>();
}
```

### initial-inputs Template (initial-inputs.html)

```html
<div class="col-md-8 d-flex align-items-end">
  <div class="form-check">
    <input
      class="form-check-input"
      type="checkbox"
      id="isGovernmentBody"
      [checked]="isGovernmentBody"
      (change)="isGovernmentBodyChange.emit($any($event.target).checked)"
    />
    <label class="form-check-label" for="isGovernmentBody">
      Filing as a Government Body ?
    </label>
  </div>
</div>
```

### new-filing.ts / edit.ts - Variable

```typescript
isGovernmentBody = false;
```

### requiresCourtFeePayment Getter

```typescript
/** Court fee step skipped for government bodies. */
get requiresCourtFeePayment(): boolean {
  return !this.isGovernmentBody;
}

get isPaymentSuccessful(): boolean {
  if (!this.requiresCourtFeePayment) return true;
  return this.paymentOutcome === "success";
}
```

### Step Navigation - next() Method

When on step 4 (documents), advance to step 6 (review) skipping payment step 5:

```typescript
if (this.step === 4) {
  if (!this.isGovernmentBody && this.docList.length > 0) {
    if (!this.hasMandatoryWpCDocuments()) {
      this.toastr.error(
        "For WP(C), upload all mandatory Main Petition indexes before proceeding.",
      );
      return;
    }
  }
  // Skip payment (step 5) for government bodies
  this.step = this.isGovernmentBody ? 6 : 5;
  this.setCaseDetailsReviewState(this.step === 6);
  return;
}
```

### Step Navigation - prev() Method

When on step 6 (review), go back to step 4 (documents) skipping payment step 5:

```typescript
prev() {
  if (this.step === 6) {
    // Skip payment (step 5) for government bodies
    this.step = this.isGovernmentBody ? 4 : 5;
  } else if (this.step === 5) {
    this.step = 4;
  } else if (this.step === 4) {
    this.step = 1;
  } else if (this.step > 1) {
    this.step--;
  }

  this.setCaseDetailsReviewState(this.step === 6);
}
```

### E-File Component Template (e-file.html)

Shows message when court fee is not required:

```html
<ng-container *ngIf="isGovernmentBody">Court fee is not required for Government body.</ng-container>
<ng-container *ngIf="!isGovernmentBody">No court fee required for this selected case type.</ng-container>
```

### Parent Component Template (new-filing.html / edit.html)

Pass isGovernmentBody to initial-inputs:

```html
<app-initial-inputs 
  [form]="initialInputsForm" 
  [isGovernmentBody]="isGovernmentBody" 
  (isGovernmentBodyChange)="isGovernmentBody = $event">
</app-initial-inputs>
```

### Download Receipt Logic

```typescript
/** Receipt PDF is only for successful online gateway payments (not offline upload flow). */
get canDownloadOnlinePaymentReceipt(): boolean {
  if (!this.requiresCourtFeePayment || this.paymentOutcome !== "success") {
    return false;
  }
  const mode = this.paymentDetails?.paymentMode ?? this.paymentMode;
  return mode === "online";
}
```

---

## OPTIONAL: Backend Government Body Field

If you want to persist the government body flag to the backend:

### Model (core/models.py - Efiling)

```python
class Efiling(BaseModel):
    # ... existing fields ...
    is_government_body = models.BooleanField(
        default=False,
        help_text="Whether this filing is by a government body and exempt from court fee"
    )
```

### Serializer (efiling_serializers.py)

```python
class EfilingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Efiling
        fields = [
            # ... existing fields ...
            'is_government_body',
        ]
```

### Usage in Payment View

```python
class PaymentInitiateView(APIView):
    def post(self, request):
        # ... existing code ...
        e_filing_id = request.data.get("application")
        
        # Skip payment for government bodies
        if e_filing_id:
            try:
                e_filing = Efiling.objects.get(pk=e_filing_id)
                if e_filing.is_government_body:
                    return Response({
                        "detail": "Court fee not required for government body filings"
                    }, status=status.HTTP_400_BAD_REQUEST)
            except Efiling.DoesNotExist:
                pass
```

### Submit Filing - Skip Payment Check

```python
@action(detail=False, methods=['post'])
def submit_for_scrutiny(self, request):
    e_filing_id = request.data.get('e_filing')
    
    try:
        e_filing = Efiling.objects.get(pk=e_filing_id)
        
        # For government bodies, skip payment validation
        if not e_filing.is_government_body:
            # Validate payment exists and is successful
            latest_payment = PaymentTransaction.objects.filter(
                application=str(e_filing_id)
            ).order_by('-created_at').first()
            
            if not latest_payment or latest_payment.status not in ['success', 'paid']:
                return Response(
                    {'error': 'Payment is required before submission'},
                    status=status.HTTP_400_BAD_REQUEST
                )
    except Efiling.DoesNotExist:
        return Response({'error': 'E-filing not found'}, status=status.HTTP_404_NOT_FOUND)
```
