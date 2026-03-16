from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from apps.core.models import Efiling
from apps.efiling.serializers.efiling_serializers import EfilingSerializer
 


class EfilingListCreateView(ListCreateAPIView):
    queryset = Efiling.objects.filter(is_active=True).order_by('-id')
    serializer_class = EfilingSerializer


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        return Response(
            {
                "id": instance.id,
                "e_filing_number": instance.e_filing_number
            },
            status=status.HTTP_201_CREATED
        )
    


class EfilingRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Efiling.objects.filter(is_active=True).order_by('-id')
    serializer_class = EfilingSerializer
