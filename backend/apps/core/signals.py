import os

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from apps.core.models import EfilingDocuments, EfilingDocumentsIndex

@receiver(pre_save, sender=EfilingDocumentsIndex)
def delete_old_file_on_update(sender, instance, **kwargs):
    if not instance.pk:
        return  # Only handle updates
    try:
        old_instance = EfilingDocumentsIndex.objects.get(pk=instance.pk)
    except EfilingDocumentsIndex.DoesNotExist:
        return

    new_file = getattr(instance, "file_part_path", None)
    if not new_file or getattr(new_file, "_committed", True):
        return

    old_file_name = getattr(old_instance.file_part_path, "name", None)
    if not old_file_name:
        return

    try:
        old_instance.file_part_path.storage.delete(old_file_name)
        return
    except Exception:
        old_file_path = getattr(old_instance.file_part_path, "path", None)
        if old_file_path and os.path.exists(old_file_path):
            os.remove(old_file_path)


@receiver(post_delete, sender=EfilingDocumentsIndex)
def delete_file_on_index_delete(sender, instance: EfilingDocumentsIndex, **kwargs):
    """
    Ensure physical PDF files are removed when an EfilingDocumentsIndex row is deleted.
    """
    file_field = getattr(instance, "file_part_path", None)
    if not file_field or not getattr(file_field, "name", None):
        return

    # Prefer storage-aware deletion.
    try:
        file_field.storage.delete(file_field.name)
        return
    except Exception:
        # Fallback to filesystem deletion for custom storages / misconfigurations.
        path = getattr(file_field, "path", None)
        if path and os.path.exists(path):
            os.remove(path)


@receiver(post_delete, sender=EfilingDocuments)
def delete_file_on_document_delete(sender, instance: EfilingDocuments, **kwargs):
    """
    Ensure physical PDF files are removed when an EfilingDocuments row is deleted.
    """
    file_field = getattr(instance, "final_document", None)
    if not file_field or not getattr(file_field, "name", None):
        return

    try:
        file_field.storage.delete(file_field.name)
        return
    except Exception:
        path = getattr(file_field, "path", None)
        if path and os.path.exists(path):
            os.remove(path)
