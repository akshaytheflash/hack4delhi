#!/usr/bin/env bash
set -e

echo "Starting deployment setup..."

cd /opt/render/project/src/backend

if [ "$RUN_MIGRATIONS" = "true" ]; then
  echo "Running database migrations..."
  alembic upgrade head
fi


echo "Checking if database needs seeding..."
python -c "
from database import SessionLocal
from models.user import User

db = SessionLocal()
user_count = db.query(User).count()
db.close()

if user_count == 0:
    print('Database is empty, seeding...')
    exit(0)
else:
    print(f'Database already has {user_count} users, skipping seed')
    exit(1)
" && python scripts/seed_data.py && python scripts/run_predictions.py || echo "Skipping seed - database already populated"

echo "Setup complete! Starting application..."

exec uvicorn main:app --host 0.0.0.0 --port $PORT
