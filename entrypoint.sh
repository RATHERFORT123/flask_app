#!/bin/sh
set -e

echo "⏳ Waiting for database..."

# simple wait (can improve later)
sleep 5

echo "🚀 Running migrations..."
flask db upgrade

echo "👤 Creating admin..."
flask create-admin

echo "🌐 Starting app..."
exec gunicorn --bind 0.0.0.0:5000 wsgi:app



