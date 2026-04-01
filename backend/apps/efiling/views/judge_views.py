from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from apps.core.models import JudgeT
from apps.efiling.serializers.judge_serializers import JudgeTSerializer

class JudgeTListCreateView(ListCreateAPIView):
    queryset = JudgeT.objects.all().order_by('-id')
    serializer_class = JudgeTSerializer

class JudgeTRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = JudgeT.objects.all()
    serializer_class = JudgeTSerializer
