import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection

with connection.cursor() as c:
    try:
        c.execute("ALTER TABLE e_filing ADD COLUMN filing_date date NULL;")
        print("Added filing_date")
    except Exception as e:
        print("filing_date exists or error:", e)
    
    try:
        c.execute("ALTER TABLE e_filing ADD COLUMN petitioner_vs_respondent varchar(600) NULL;")
        print("Added PVR")
    except Exception as e:
        print("PVR exists or error:", e)
print("Done")
