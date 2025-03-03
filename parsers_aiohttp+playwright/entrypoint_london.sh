#!/bin/sh

set -e
python /app/db/postgress_create_models.py
exec python /app/London/main.py