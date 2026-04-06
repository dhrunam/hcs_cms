from rest_framework.generics import ListAPIView

from apps.core.models import BudgetHeadT
from apps.efiling.serializers.budget_head_serializers import (
    BudgetHeadTSerializer,
)


class BudgetHeadTListView(ListAPIView):
    serializer_class = BudgetHeadTSerializer

    def get_queryset(self):
        queryset = BudgetHeadT.objects.all().order_by('-id')
        case_type = self.request.query_params.get('case_type')
        if case_type not in (None, '', 'null'):
            queryset = queryset.filter(case_type_id=case_type)
        return queryset