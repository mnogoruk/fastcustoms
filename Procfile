release: python manage.py makemigrations
release: python manage.py migrate
web: gunicorn fastcustoms.wsgi:application --preload