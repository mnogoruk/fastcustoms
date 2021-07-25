release: python manage.py makemigrations
release: python manage.py migrate --fake
web: gunicorn fastcustoms.wsgi:application --preload