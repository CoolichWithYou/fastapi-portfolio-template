#!/bin/sh

until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
  echo "Waiting for postgres..."
  sleep 2
done

exec uvicorn server.main:app --host 0.0.0.0 --port 8000
