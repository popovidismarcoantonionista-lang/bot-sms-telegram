#!/bin/bash
# Start script for Railway deployment

echo "🚀 Starting Bot SMS Telegram..."

# Initialize database
echo "📊 Initializing database..."
python -c "from database import db; db.init_db()" || echo "⚠️  Database already initialized"

# Start bot
echo "🤖 Starting Telegram bot..."
python bot.py
