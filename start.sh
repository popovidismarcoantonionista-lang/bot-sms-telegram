#!/bin/bash

echo "🚀 Iniciando Bot no Railway..."

# Verificar variáveis de ambiente
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ ERRO: TELEGRAM_BOT_TOKEN não configurado!"
    exit 1
fi

echo "✅ Token encontrado"
echo "✅ Iniciando bot..."

# Executar bot
python bot.py
