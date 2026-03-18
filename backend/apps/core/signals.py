from django.db.models.signals import pre_save
from django.dispatch import receiver
from apps.core.models import EfilingDocumentsIndex
import os

@receiver(pre_save, sender=EfilingDocumentsIndex)
def delete_old_file_on_update(sender, instance, **kwargs):
    if not instance.pk:
        return  # Only handle updates
    try:
        old_instance = EfilingDocumentsIndex.objects.get(pk=instance.pk)
    except EfilingDocumentsIndex.DoesNotExist:
        return
    old_file = old_instance.file_part_path.path if old_instance.file_part_path else None
    new_file = instance.file_part_path.path if instance.file_part_path else None
    if old_file and new_file and old_file != new_file:
        if os.path.exists(old_file):
            os.remove(old_file)
