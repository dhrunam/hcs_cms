from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from apps.core.models import Efiling
from apps.efiling.serializers.efiling_serializers import EfilingSerializer
from apps.efiling.review_utils import derive_filing_status, submit_documents_for_scrutiny

 
class EfilingListCreateView(ListCreateAPIView):
    queryset = Efiling.objects.all()
    serializer_class = EfilingSerializer

    def get_queryset(self):
        qs = Efiling.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        is_draft = self.request.query_params.get('is_draft')
        if is_active is not None:
            # treat "true"/"1" as True
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        if is_draft is not None:
            qs = qs.filter(is_draft=is_draft.lower() in ['true', '1'])
        return qs



  

    

class EfilingRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Efiling.objects.all()
    serializer_class = EfilingSerializer
    def get_queryset(self):
        qs = Efiling.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            # treat "true"/"1" as True
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
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


