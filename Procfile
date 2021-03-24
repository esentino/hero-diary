release: python manage.py migrate
web: gunicorn -b 0.0.0.0:$PORT --workers 1 hero_diary.wsgi:application
worker: python worker.py
