#!/bin/bash
# Start script for Railway deployment - OPTIMIZED

echo "🚀 Starting Bot SMS Telegram..."

# Initialize database
echo "📊 Initializing database..."
python -c "from database import db; db.init_db()" || echo "⚠️  Database already initialized"

# Start worker in background (verifies deposits)
echo "⚙️  Starting deposit worker..."
python worker.py &
WORKER_PID=$!

# Wait a moment for worker to initialize
sleep 2

# Start bot
echo "🤖 Starting Telegram bot..."
python bot.py

# If bot exits, kill worker
kill $WORKER_PID 2>/dev/null
