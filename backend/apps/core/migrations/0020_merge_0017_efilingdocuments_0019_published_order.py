# Merge parallel core branches (casetype/efilingdocuments vs orderdetailsa chain).

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0017_efilingdocuments_document_filing_submitted_at"),
        ("core", "0019_efilingdocumentsindex_published_order_at"),
    ]

    operations = []
