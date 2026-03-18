from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.db import transaction

from apps.core.models import EfilingDocumentsIndex, EfilingDocumentsScrutinyHistory
from apps.efiling.serializers.efiling_document_index import (
    EfilingDocumentsIndexSerializer,
)


class EfilingDocumentsIndexListCreateView(ListCreateAPIView):
    
    serializer_class = EfilingDocumentsIndexSerializer
    def get_queryset(self):
        qs = EfilingDocumentsIndex.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        return qs

    def perform_create(self, serializer):
        with transaction.atomic():
            instance = serializer.save()
            EfilingDocumentsScrutinyHistory.objects.create(
                efiling_document_index=instance,
                recieved_at=instance.created_at,
            )


class EfilingDocumentsIndexRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = EfilingDocumentsIndexSerializer
    def get_queryset(self):
        qs = EfilingDocumentsIndex.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            # treat "true"/"1" as True
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        return qs

    def update(self, request, *args, **kwargs):        
        with transaction.atomic():
            instance = self.get_object()
            old_file = instance.file_part_path.path if instance.file_part_path else None
            # Delete old file before upload
            if old_file and 'file_part_path' in request.FILES:
                import os
                if os.path.exists(old_file):
                    os.remove(old_file)
            response = super().update(request, *args, **kwargs)
            instance.refresh_from_db()
            new_file = instance.file_part_path.path if instance.file_part_path else None
            if old_file and new_file and old_file != new_file:
                import os
                if os.path.exists(old_file):
                    os.remove(old_file)
            EfilingDocumentsScrutinyHistory.objects.create(
                efiling_document_index=instance,
                recieved_at=instance.updated_at,
            )
        return response

    def partial_update(self, request, *args, **kwargs):        
        with transaction.atomic():
            instance = self.get_object()
            old_file = instance.file_part_path.path if instance.file_part_path else None
            # Delete old file before upload
            if old_file and 'file_part_path' in request.FILES:
                import os
                if os.path.exists(old_file):
                    os.remove(old_file)
            response = super().partial_update(request, *args, **kwargs)
            instance.refresh_from_db()
            new_file = instance.file_part_path.path if instance.file_part_path else None
            if old_file and new_file and old_file != new_file:
                import os
                if os.path.exists(old_file):
                    os.remove(old_file)
            EfilingDocumentsScrutinyHistory.objects.create(
                efiling_document_index=instance,
                recieved_at=instance.updated_at,
            )
        return response

