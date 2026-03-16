from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from apps.core.models import EfilingCaseDetails
from apps.efiling.serializers.efiling_case_details_serializers import EfilingCaseDetailsSerializer


class EfilingCaseDetailsListCreateView(ListCreateAPIView):
    queryset = EfilingCaseDetails.objects.filter(is_active=True).order_by('-id')
    serializer_class = EfilingCaseDetailsSerializer


class EfilingCaseDetailsRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = EfilingCaseDetails.objects.filter(is_active=True).order_by('-id')
    serializer_class = EfilingCaseDetailsSerializer
