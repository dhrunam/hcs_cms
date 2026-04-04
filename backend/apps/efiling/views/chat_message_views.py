from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView

from apps.core.models import ChatMessage, Efiling
from apps.efiling.serializers.chat_message_serializers import ChatMessageSerializer


class ChatMessageListCreateView(ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    pagination_class = None

    def get_queryset(self):
        filing = get_object_or_404(Efiling, pk=self.kwargs["pk"])
        return (
            ChatMessage.objects.filter(e_filing=filing, is_active=True)
            .select_related("sender")
            .order_by("created_at", "id")
        )

    def perform_create(self, serializer):
        filing = get_object_or_404(Efiling, pk=self.kwargs["pk"])
        sender = self.request.user if self.request.user.is_authenticated else None
        serializer.save(e_filing=filing, sender=sender, created_by=sender, updated_by=sender)