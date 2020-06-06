release: python manage.py migrate
web: uvicorn hero_diary.asgi:application --port $PORT --host 0.0.0.0