from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.core.models import Efiling
from apps.efiling.serializers.efiling_serializers import EfilingSerializer
from apps.efiling.review_utils import (
    derive_filing_status,
    finalize_scrutiny_submission,
    submit_documents_for_scrutiny,
)


def parse_bool(value):
    """
    Parse a query parameter string to a boolean.
    Accepts: 'true', '1', 'yes' -> True
    Accepts: 'false', '0', 'no' -> False
    Returns: None if value is None or unrecognized.
    """
    if value is None:
        return None
    value_str = str(value).lower().strip()
    if value_str in ('true', '1', 'yes'):
        return True
    elif value_str in ('false', '0', 'no'):
        return False
    return None

 
class EfilingListCreateView(ListCreateAPIView):
    queryset = Efiling.objects.all()
    serializer_class = EfilingSerializer

    def get_queryset(self):
        qs = Efiling.objects.all().order_by('-id')
        is_active = parse_bool(self.request.query_params.get('is_active'))
        is_draft = parse_bool(self.request.query_params.get('is_draft'))
        status = self.request.query_params.get('status')
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        if is_draft is not None:
            qs = qs.filter(is_draft=is_draft)
        if status is not None:
            # typo handling: ACCPETED -> ACCEPTED.
            if status.strip().upper() == 'ACCEPTED':
                qs = qs.filter(status='ACCEPTED')
            else:
                # all non-accepted records for any other status value.
                qs = qs.exclude(status='ACCEPTED')
        return qs



  

    

class EfilingRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Efiling.objects.all()
    serializer_class = EfilingSerializer
    def get_queryset(self):
        qs = Efiling.objects.all().order_by('-id')
        is_active = parse_bool(self.request.query_params.get('is_active'))
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        return qs

    def partial_update(self, request, *args, **kwargs):
        filing = self.get_object()
        was_draft = filing.is_draft
        response = super().partial_update(request, *args, **kwargs)
        filing.refresh_from_db()

        if was_draft and not filing.is_draft:
            submit_documents_for_scrutiny(
                filing,
                user=request.user if request.user.is_authenticated else None,
            )
        else:
            derive_filing_status(filing)

        return response


class EfilingSubmitApprovedView(APIView):
    def post(self, request, pk):
        filing = get_object_or_404(Efiling.objects.all(), pk=pk)
        filing = finalize_scrutiny_submission(
            filing,
            user=request.user if request.user.is_authenticated else None,
        )
        return Response(EfilingSerializer(filing).data)


