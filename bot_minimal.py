#!/usr/bin/env python3
"""
BOT MINIMALISTA - Versão simples para teste
Se este não funcionar, o problema é no token ou internet
"""

import asyncio
import os
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

if not TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN não configurado!")
    exit(1)

print(f"🔑 Token: {TOKEN[:15]}...")

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start mais simples possível"""
    print(f"📨 Comando /start recebido de: {update.effective_user.username}")

    await update.message.reply_text(
        "✅ BOT ESTÁ FUNCIONANDO!\n\n"
        "Se você está vendo esta mensagem, o bot está OK.\n"
        "O problema estava na versão anterior."
    )

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /test"""
    await update.message.reply_text("✅ Teste OK!")

async def main():
    print("🚀 Iniciando bot minimalista...")

    # Criar aplicação
    app = Application.builder().token(TOKEN).build()

    # Adicionar handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", test))

    # Verificar bot
    bot_info = await app.bot.get_me()
    print(f"✅ Bot conectado: @{bot_info.username}")
    print(f"📱 Aguardando comandos...")
    print(f"\n💡 Envie /start para @{bot_info.username} no Telegram")

    # Iniciar
    await app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot encerrado")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        print("\n💡 Execute o diagnostico.py para mais detalhes")
