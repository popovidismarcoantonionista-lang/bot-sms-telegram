#!/usr/bin/env python3
"""
Bot SMS Telegram - RAILWAY VERSION
Simplificado e otimizado para produção
"""

import logging
import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Import config
try:
    from config import (
        TELEGRAM_BOT_TOKEN, 
        ADMIN_IDS, 
        SMS_ACTIVATE_API_KEY,
        REFERRAL_BONUS
    )
    logger.info("✅ Config importado com sucesso")
except Exception as e:
    logger.error(f"❌ Erro ao importar config: {e}")
    raise

# Import database
try:
    from database import Database
    db = Database()
    logger.info("✅ Database importado")
except Exception as e:
    logger.error(f"❌ Erro ao importar database: {e}")
    # Continuar sem database por enquanto
    db = None

# ==========================================================================
# COMANDOS
# ==========================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    try:
        user = update.effective_user
        logger.info(f"👤 /start de {user.username} (ID: {user.id})")

        # Menu
        keyboard = [
            [InlineKeyboardButton("💰 Ver Saldo", callback_data="saldo")],
            [InlineKeyboardButton("📱 Comprar SMS", callback_data="comprar")],
            [InlineKeyboardButton("💳 Depositar", callback_data="depositar")],
            [InlineKeyboardButton("ℹ️ Ajuda", callback_data="ajuda")]
        ]

        if user.id in ADMIN_IDS:
            keyboard.append([InlineKeyboardButton("🔐 Admin", callback_data="admin")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"👋 Olá, **{user.first_name}**!\n\n"
            "🤖 Bot SMS Telegram\n\n"
            "Escolha uma opção:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"❌ Erro em /start: {e}")
        await update.message.reply_text("❌ Erro. Tente novamente.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler de botões"""
    query = update.callback_query
    await query.answer()

    try:
        data = query.data

        if data == "saldo":
            await query.edit_message_text("💰 Saldo: R$ 0.00\n\nUse /depositar para adicionar créditos")

        elif data == "comprar":
            await query.edit_message_text("📱 Compra de SMS em desenvolvimento...")

        elif data == "depositar":
            keyboard = [
                [InlineKeyboardButton("💳 R$ 10", callback_data="dep_10")],
                [InlineKeyboardButton("💳 R$ 20", callback_data="dep_20")],
                [InlineKeyboardButton("💳 R$ 50", callback_data="dep_50")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "💳 Escolha o valor:", 
                reply_markup=reply_markup
            )

        elif data == "ajuda":
            await query.edit_message_text(
                "❓ **Ajuda**\n\n"
                "Use /start para ver o menu\n"
                "Use /saldo para ver seu saldo",
                parse_mode="Markdown"
            )

        elif data.startswith("dep_"):
            amount = data.split("_")[1]
            await query.edit_message_text(
                f"💳 Depósito de R$ {amount},00\n\n"
                "🔄 Gerando pagamento...\n"
                "(Em desenvolvimento)"
            )

    except Exception as e:
        logger.error(f"❌ Erro no callback: {e}")

# ==========================================================================
# MAIN
# ==========================================================================

async def main():
    """Função principal"""
    try:
        logger.info("🚀 Iniciando bot...")

        # Inicializar database
        if db:
            await db.initialize()
            logger.info("✅ Database inicializado")

        # Criar app
        app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        # Handlers
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CallbackQueryHandler(button_callback))

        # Info do bot
        bot_info = await app.bot.get_me()
        logger.info(f"✅ Bot conectado: @{bot_info.username}")
        logger.info(f"📱 ID: {bot_info.id}")
        logger.info(f"👥 Admins: {len(ADMIN_IDS)}")
        logger.info("🎯 Bot pronto! Aguardando mensagens...")

        # Iniciar
        await app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

    except Exception as e:
        logger.error(f"❌ ERRO FATAL: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot encerrado pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
