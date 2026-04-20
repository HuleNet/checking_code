#!/bin/sh

echo "Waiting for PostgreSQL..."

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done

echo "PostgreSQL is ready"

echo "Waiting for RabbitMQ..."

while ! nc -z $BROKER_HOST $BROKER_PORT; do
  sleep 1
done

echo "RabbitMQ is ready"

echo "Running migrations..."
uv run alembic upgrade head

echo "Starting app..."
exec "$@"