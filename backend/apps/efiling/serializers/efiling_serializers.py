from rest_framework import serializers

from apps.core.models import CaseTypeT, Efiling
from apps.efiling.party_display import build_petitioner_vs_respondent


class EfilingCaseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseTypeT
        fields = ['id', 'case_type', 'type_name', 'full_form', 'annexure_type']


class EfilingSerializer(serializers.ModelSerializer):
    case_type = serializers.PrimaryKeyRelatedField(
        queryset=CaseTypeT.objects.all(),
        required=False,
        allow_null=True,
    )
    petitioner_vs_respondent = serializers.SerializerMethodField(read_only=True)
    latest_chat_message_id = serializers.SerializerMethodField(read_only=True)
    latest_chat_message_at = serializers.SerializerMethodField(read_only=True)
    latest_chat_is_from_current_user = serializers.SerializerMethodField(read_only=True)
    has_payment_objection = serializers.SerializerMethodField(read_only=True)
    payment_objection_amount = serializers.SerializerMethodField(read_only=True)
    objection_resolved_by_payment = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Efiling
        fields = [
            'id',
            'case_type',
            'bench',
            'petitioner_name',
            'petitioner_contact',
            'e_filing_number',
            'case_number',
            'is_draft',
            'status',
            'accepted_at',
            'is_active',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
            'petitioner_vs_respondent',
            'latest_chat_message_id',
            'latest_chat_message_at',
            'latest_chat_is_from_current_user',
            'has_payment_objection',
            'payment_objection_amount',
            'objection_resolved_by_payment',
        ]
        read_only_fields = [
            'id',
            'e_filing_number',
            'case_number',
            'status',
            'accepted_at',
            'created_at',
            'updated_at',
            'petitioner_vs_respondent',
            'latest_chat_message_id',
            'latest_chat_message_at',
            'latest_chat_is_from_current_user',
            'has_payment_objection',
            'payment_objection_amount',
            'objection_resolved_by_payment',
        ]

    def get_petitioner_vs_respondent(self, obj):
        preferred = str(getattr(obj, "petitioner_name", None) or "").strip()
        if preferred:
            return preferred
        return build_petitioner_vs_respondent(
            obj,
            fallback_petitioner_name=getattr(obj, "petitioner_name", None) or "",
        )

    def get_latest_chat_message_id(self, obj):
        latest_message = obj.chat_messages.filter(is_active=True).order_by('-created_at', '-id').first()
        return latest_message.id if latest_message else None

    def get_latest_chat_message_at(self, obj):
        latest_message = obj.chat_messages.filter(is_active=True).order_by('-created_at', '-id').first()
        return latest_message.created_at if latest_message else None

    def get_latest_chat_is_from_current_user(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        latest_message = obj.chat_messages.filter(is_active=True).order_by('-created_at', '-id').first()
        if not latest_message or not latest_message.sender_id:
            return False
        return latest_message.sender_id == request.user.id

    def get_has_payment_objection(self, obj):
        """Check if there's a pending payment objection for this e-filing that hasn't been resolved by a matching payment."""
        from apps.efiling.models import PaymentObjection
        from apps.payment.models import PaymentTransaction
        from django.utils import timezone
        
        pending_objection = PaymentObjection.objects.filter(
            e_filing=obj,
            status=PaymentObjection.Status.PENDING
        ).order_by('-raised_at').first()
        
        if not pending_objection:
            return False
        
        required_amount = float(pending_objection.court_fee_amount)
        raised_at = pending_objection.raised_at
        if raised_at.tzinfo is None:
            raised_at = timezone.make_aware(raised_at, timezone.utc)
        
        successful_payments = PaymentTransaction.objects.filter(
            application=str(obj.id)
        ).filter(
            status__iregex=r'^(success|paid|complete|ok)$'
        ).filter(
            created_at__gt=raised_at
        )
        
        for payment in successful_payments:
            payment_amount = float(payment.amount or 0)
            if payment_amount >= required_amount:
                return False
        
        return True

    def get_payment_objection_amount(self, obj):
        """Get the court fee amount from the latest unresolved payment objection."""
        from apps.efiling.models import PaymentObjection
        from apps.payment.models import PaymentTransaction
        from django.utils import timezone
        
        pending_objection = PaymentObjection.objects.filter(
            e_filing=obj,
            status=PaymentObjection.Status.PENDING
        ).order_by('-raised_at').first()
        
        if not pending_objection:
            return None
        
        required_amount = float(pending_objection.court_fee_amount)
        raised_at = pending_objection.raised_at
        if raised_at.tzinfo is None:
            raised_at = timezone.make_aware(raised_at, timezone.utc)
        
        successful_payments = PaymentTransaction.objects.filter(
            application=str(obj.id)
        ).filter(
            status__iregex=r'^(success|paid|complete|ok)$'
        ).filter(
            created_at__gt=raised_at
        )
        
        for payment in successful_payments:
            payment_amount = float(payment.amount or 0)
            if payment_amount >= required_amount:
                return None
        
        return required_amount

    def get_objection_resolved_by_payment(self, obj):
        """Return payment info if the objection was resolved by a successful payment matching the required amount."""
        import logging
        logger = logging.getLogger(__name__)
        
        from apps.efiling.models import PaymentObjection
        from apps.payment.models import PaymentTransaction
        from django.utils import timezone
        
        pending_objection = PaymentObjection.objects.filter(
            e_filing=obj,
            status=PaymentObjection.Status.PENDING
        ).order_by('-raised_at').first()
        
        if not pending_objection:
            logger.info(f"[ObjectionDebug] No pending objection for efiling {obj.id}")
            return None
        
        logger.info(f"[ObjectionDebug] Found pending objection {pending_objection.id} for efiling {obj.id}, raised_at={pending_objection.raised_at}, amount={pending_objection.court_fee_amount}")
        
        required_amount = float(pending_objection.court_fee_amount)
        raised_at = pending_objection.raised_at
        if raised_at.tzinfo is None:
            raised_at = timezone.make_aware(raised_at, timezone.utc)
        
        successful_payments = PaymentTransaction.objects.filter(
            application=str(obj.id)
        ).filter(
            status__iregex=r'^(success|paid|complete|ok)$'
        ).filter(
            created_at__gt=raised_at
        ).order_by('created_at')
        
        logger.info(f"[ObjectionDebug] Query: application={str(obj.id)}, created_at__gt={raised_at}")
        logger.info(f"[ObjectionDebug] All payments after raised_at: {[(p.id, p.amount, p.status, p.created_at) for p in successful_payments]}")
        
        for payment in successful_payments:
            payment_amount = float(payment.amount or 0)
            logger.info(f"[ObjectionDebug] Checking payment {payment.id}: amount={payment_amount}, required={required_amount}")
            if payment_amount >= required_amount:
                result = {
                    'payment_id': payment.id,
                    'txn_id': payment.txn_id,
                    'amount': payment_amount,
                    'payment_datetime': (payment.updated_at or payment.created_at).isoformat() if (payment.updated_at or payment.created_at) else None,
                    'status': payment.status,
                }
                logger.info(f"[ObjectionDebug] Payment {payment.id} resolves objection, returning: {result}")
                return result
        
        logger.info(f"[ObjectionDebug] No payment found that satisfies required amount {required_amount}")
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['case_type'] = (
            EfilingCaseTypeSerializer(instance.case_type).data
            if instance.case_type_id
            else None
        )
        return data
