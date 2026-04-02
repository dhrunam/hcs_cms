import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

def manually_fake_apply(app, migration):
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, NOW())",
            [app, migration]
        )
    print(f"Manually marked {app}.{migration} as applied.")

if __name__ == "__main__":
    manually_fake_apply('core', '0033_initial_models')
