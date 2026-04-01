from rest_framework.views import APIView
from rest_framework.response import Response
from apps.core.models import BenchT

class BenchDistinctListView(APIView):
    """
    Returns a list of benches, distinct by bench_code and bench_name.
    """
    def get(self, request, *args, **kwargs):
        benches = BenchT.objects.values('bench_code', 'bench_name').distinct().order_by('bench_code')
        return Response(list(benches))
