#!/usr/bin/env bash

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate

gunicorn lms.wsgi:application --bind 0.0.0.0:$PORT