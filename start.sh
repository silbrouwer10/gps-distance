#!/usr/bin/env bash
set -o errexit

gunicorn myproject.wsgi:application --bind 0.0.0.0:$PORT
