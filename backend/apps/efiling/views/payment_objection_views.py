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
