#!/bin/sh

set -e

echo "Waiting for PostgreSQL on $DB_HOST:$DB_PORT..."

while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -q; do
  echo "PostgreSQL is not ready - sleeping 1 second"
  sleep 1
done

echo "PostgreSQL is ready - continuing..."

python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
python manage.py create_placeholders

python manage.py shell <<EOF
import os
from django.contrib.auth import get_user_model

User = get_user_model()
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'adminpassword')

if not User.objects.filter(email=email).exists():
    print(f"Creating superuser with email '{email}'...")
    User.objects.create_superuser(email=email, password=password)
    print(f"Superuser '{email}' created.")
else:
    print(f"Superuser '{email}' already exists.")
EOF

python manage.py rqworker default &

exec gunicorn core.wsgi:application --bind 0.0.0.0:8000
