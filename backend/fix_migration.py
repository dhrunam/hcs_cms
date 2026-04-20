import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django
django.setup()
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("DELETE FROM django_migrations WHERE app = 'efiling' AND name = '0002_paymentobjection'")
    print(f"Deleted {cursor.rowcount} row(s)")
