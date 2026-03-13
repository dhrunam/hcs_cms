from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.core.models import EfilingCaseDetails
from apps.efiling.serializers.efiling_case_details_serializers import EfilingCaseDetailsSerializer


class EfilingCaseDetailsListCreateView(ListCreateAPIView):
    queryset = EfilingCaseDetails.objects.all()
    serializer_class = EfilingCaseDetailsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class EfilingCaseDetailsRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = EfilingCaseDetails.objects.all()
    serializer_class = EfilingCaseDetailsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
