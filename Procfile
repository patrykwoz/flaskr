web: gunicorn app:flask_app
worker: celery -A app worker --loglevel=info