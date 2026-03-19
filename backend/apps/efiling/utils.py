from django.db import transaction
from apps.efiling.models import EfilingNumberSequence

def get_next_efiling_number():

    from django.utils import timezone
    with transaction.atomic():
        year=timezone.now().year
        seq,created=EfilingNumberSequence.objects.select_for_update().get_or_create(year=year,
        defaults={
            'last_sequence':0
        },
        )

        seq.last_sequence+=1
        seq.save(update_fields=['last_sequence'])
        n=seq.last_sequence
    return f"ASK{n:09d}C{year}{n:05d}"