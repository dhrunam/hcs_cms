from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.bench_config import get_bench_configurations


class BenchDistinctListView(APIView):
    """
    Benches available for case registration: same merged active configs as reader routing.
    Each item includes bench_key (canonical storage), bench_code, bench_name, label.
    """

    def get(self, request, *args, **kwargs):
        items = []
        for cfg in get_bench_configurations():
            items.append(
                {
                    "bench_key": cfg.bench_key,
                    "bench_code": cfg.bench_code,
                    "bench_name": cfg.bench_name,
                    "label": cfg.label,
                }
            )
        return Response(items)
