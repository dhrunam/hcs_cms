from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from apps.core.models import BenchT
from apps.efiling.serializers.bench_serializers import BenchTSerializer

class BenchTListCreateView(ListCreateAPIView):
    queryset = BenchT.objects.all().order_by('-id')
    serializer_class = BenchTSerializer

class BenchTRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = BenchT.objects.all()
    serializer_class = BenchTSerializer
