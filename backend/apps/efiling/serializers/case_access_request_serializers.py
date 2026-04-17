from __future__ import annotations

from rest_framework import serializers

from apps.core.models import CaseAccessRequest, Efiling, EfilerDocumentAccess


class CaseAccessRequestSerializer(serializers.ModelSerializer):
    e_filing_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = CaseAccessRequest
        fields = "__all__"
        read_only_fields = (
            "advocate",
            "e_filing",
            "e_filing_id",
            "is_active",
            "created_by",
            "updated_by",
            "status",
            "rejection_reason",
            "reviewed_by",
            "reviewed_at",
            "approved_access",
            "resubmission_of",
        )

    def validate_case_number(self, value: str) -> str:
        case_number = (value or "").strip()
        if not case_number:
            raise serializers.ValidationError("Case number is required.")
        return case_number

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        case_number = (attrs.get("case_number") or "").strip()
        filing = (
            Efiling.objects.filter(case_number__iexact=case_number, is_draft=False)
            .order_by("-id")
            .first()
        )
        if filing is None:
            raise serializers.ValidationError({"case_number": "No registered case found for this case number."})

        if filing.created_by_id == getattr(user, "id", None):
            raise serializers.ValidationError({"case_number": "This case is already part of your filings."})

        has_access = EfilerDocumentAccess.objects.filter(
            e_filing=filing,
            efiler=user,
            is_active=True,
        ).exists()
        if has_access:
            raise serializers.ValidationError({"case_number": "You already have access to this case."})

        pending_exists = CaseAccessRequest.objects.filter(
            advocate=user,
            e_filing=filing,
            status=CaseAccessRequest.Status.PENDING,
            is_active=True,
        ).exists()
        if pending_exists:
            raise serializers.ValidationError(
                {"case_number": "You already have a pending request for this case."}
            )

        attrs["e_filing"] = filing
        attrs["case_number"] = filing.case_number or case_number
        return attrs
