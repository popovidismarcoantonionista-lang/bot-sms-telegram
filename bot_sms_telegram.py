#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot de Vendas de SMS - Versão Corrigida
Sem uso de Updater (que causa AttributeError)
"""

import os
import json
import requests
import logging
from datetime import datetime
from typing import Dict, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler
)

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============== CONFIGURAÇÕES ==============
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7958563749:AAGUWtp2ISNcegnOHAr1Hfqu_dpigJPJR8s")
PLUGGY_CLIENT_ID = os.getenv("PLUGGY_CLIENT_ID", "3d15ed55-b74a-4b7c-8bcc-430e80cf01ab")
PLUGGY_CLIENT_SECRET = os.getenv("PLUGGY_CLIENT_SECRET", "ccef002e-7935-452b-ace8-dde1db125e81")
SMS_ACTIVATE_API_KEY = os.getenv("SMS_ACTIVATE_API_KEY", "58f78469017177b5defd637edA3983d1")
SMS_ACTIVATE_BASE_URL = "https://api.sms-activate.org/stubs/handler_api.php"

# Preços
PRECO_CATEGORIAS = {
    "basico": {"preco": 0.60, "servicos": ["WhatsApp", "Telegram", "Discord"]},
    "padrao": {"preco": 1.00, "servicos": ["Instagram", "Facebook", "Twitter", "TikTok"]},
    "premium": {"preco": 2.50, "servicos": ["Google", "Microsoft", "Amazon", "PayPal"]}
}
DEPOSITO_MINIMO = 1.00

# Estados
ESCOLHER_CATEGORIA, ESCOLHER_SERVICO = range(2)

# ============== DATABASE ==============
DATABASE_FILE = "database.json"

def carregar_database():
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def salvar_database(db):
    try:
        with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erro ao salvar database: {e}")

USER_DATABASE = carregar_database()

def get_usuario(user_id: int) -> Dict:
    user_id_str = str(user_id)
    if user_id_str not in USER_DATABASE:
        USER_DATABASE[user_id_str] = {
            "saldo": 0.0,
            "historico_compras": [],
            "numeros_ativos": []
        }
        salvar_database(USER_DATABASE)
    return USER_DATABASE[user_id_str]

def atualizar_saldo(user_id: int, valor: float):
    user_id_str = str(user_id)
    usuario = get_usuario(user_id)
    usuario["saldo"] += valor
    USER_DATABASE[user_id_str] = usuario
    salvar_database(USER_DATABASE)

# ============== SMS ACTIVATE ==============
def obter_numero_sms(servico: str) -> Optional[Dict]:
    try:
        servico_map = {
            "WhatsApp": "wa", "Telegram": "tg", "Discord": "ds",
            "Instagram": "ig", "Facebook": "fb", "Twitter": "tw",
            "TikTok": "tt", "Google": "go", "Microsoft": "mm",
            "Amazon": "am", "PayPal": "pp"
        }

        codigo = servico_map.get(servico, "wa")

        response = requests.get(
            SMS_ACTIVATE_BASE_URL,
            params={
                "api_key": SMS_ACTIVATE_API_KEY,
                "action": "getNumber",
                "service": codigo,
                "country": 132
            },
            timeout=10
        )

        if response.status_code == 200:
            parts = response.text.split(":")
            if len(parts) == 3 and parts[0] == "ACCESS_NUMBER":
                return {
                    "activation_id": parts[1],
                    "numero": parts[2],
                    "servico": servico
                }

        logger.error(f"Erro ao obter número: {response.text}")
        return None
    except Exception as e:
        logger.error(f"Exceção: {e}")
        return None

def obter_codigo_sms(activation_id: str) -> Optional[str]:
    try:
        response = requests.get(
            SMS_ACTIVATE_BASE_URL,
            params={
                "api_key": SMS_ACTIVATE_API_KEY,
                "action": "getStatus",
                "id": activation_id
            },
            timeout=10
        )

        if response.status_code == 200:
            parts = response.text.split(":")
            if len(parts) == 2 and parts[0] == "STATUS_OK":
                return parts[1]
            elif response.text == "STATUS_WAIT_CODE":
                return "AGUARDANDO"
        return None
    except Exception as e:
        logger.error(f"Erro: {e}")
        return None

def cancelar_numero_sms(activation_id: str) -> bool:
    try:
        response = requests.get(
            SMS_ACTIVATE_BASE_URL,
            params={
                "api_key": SMS_ACTIVATE_API_KEY,
                "action": "setStatus",
                "id": activation_id,
                "status": 8
            },
            timeout=10
        )
        return response.status_code == 200 and "ACCESS_CANCEL" in response.text
    except:
        return False

# ============== COMANDOS ==============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    usuario = get_usuario(user.id)

    mensagem = f"""
🎉 *Bem-vindo ao Bot de SMS!* 🎉

Olá {user.first_name}!

💰 *Saldo*: R$ {usuario['saldo']:.2f}

📱 *Preços*:
• R$ 0,60 - WhatsApp, Telegram, Discord
• R$ 1,00 - Instagram, Facebook, Twitter
• R$ 2,50 - Google, Microsoft, Amazon

⚡ *Comandos*:
/comprar - Comprar número
/depositar - Adicionar saldo
/saldo - Ver saldo
/historico - Histórico
/ajuda - Ajuda
    """

    await update.message.reply_text(mensagem, parse_mode="Markdown")

async def saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    usuario = get_usuario(user.id)

    await update.message.reply_text(
        f"💰 *Saldo*: R$ {usuario['saldo']:.2f}\n\nUse /depositar para adicionar.",
        parse_mode="Markdown"
    )

async def depositar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("R$ 5", callback_data="dep_5")],
        [InlineKeyboardButton("R$ 10", callback_data="dep_10")],
        [InlineKeyboardButton("R$ 20", callback_data="dep_20")],
        [InlineKeyboardButton("R$ 50", callback_data="dep_50")]
    ]

    await update.message.reply_text(
        f"💳 *Adicionar Saldo*\n\nSelecione o valor:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def processar_deposito(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("dep_"):
        valor = float(query.data.split("_")[1])

        mensagem = f"""
✅ *Pagamento*

Valor: R$ {valor:.2f}

📱 PIX: `seu-pix@email.com`

Envie comprovante para @seu_usuario

⏰ Crédito em 5 min
        """

        await query.edit_message_text(mensagem, parse_mode="Markdown")

async def comprar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📱 R$ 0,60", callback_data="cat_basico")],
        [InlineKeyboardButton("📱 R$ 1,00", callback_data="cat_padrao")],
        [InlineKeyboardButton("📱 R$ 2,50", callback_data="cat_premium")]
    ]

    user = update.effective_user
    usuario = get_usuario(user.id)

    await update.message.reply_text(
        f"🛒 *Comprar*\n\nSaldo: R$ {usuario['saldo']:.2f}\n\nEscolha:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def escolher_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("cat_"):
        categoria = query.data.split("_")[1]
        context.user_data['categoria'] = categoria

        servicos = PRECO_CATEGORIAS[categoria]["servicos"]
        preco = PRECO_CATEGORIAS[categoria]["preco"]

        keyboard = [[InlineKeyboardButton(f"📱 {s}", callback_data=f"srv_{s}")] for s in servicos]

        await query.edit_message_text(
            f"📱 *{categoria.title()}* - R$ {preco:.2f}\n\nEscolha:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

        return ESCOLHER_SERVICO

async def escolher_servico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    usuario = get_usuario(user.id)

    if query.data.startswith("srv_"):
        servico = query.data.split("_")[1]
        categoria = context.user_data.get('categoria', 'basico')
        preco = PRECO_CATEGORIAS[categoria]["preco"]

        if usuario['saldo'] < preco:
            await query.edit_message_text(
                f"❌ *Saldo Insuficiente*\n\nPreço: R$ {preco:.2f}\nSaldo: R$ {usuario['saldo']:.2f}",
                parse_mode="Markdown"
            )
            return ConversationHandler.END

        await query.edit_message_text("⏳ Buscando número...")

        numero_info = obter_numero_sms(servico)

        if numero_info:
            atualizar_saldo(user.id, -preco)

            usuario['numeros_ativos'].append({
                "activation_id": numero_info['activation_id'],
                "numero": numero_info['numero'],
                "servico": servico,
                "data": datetime.now().isoformat(),
                "preco": preco
            })
            salvar_database(USER_DATABASE)

            keyboard = [
                [InlineKeyboardButton("🔄 Verificar", callback_data=f"ver_{numero_info['activation_id']}")],
                [InlineKeyboardButton("❌ Cancelar", callback_data=f"can_{numero_info['activation_id']}")]
            ]

            await query.edit_message_text(
                f"✅ *Número Adquirido!*\n\n📱 `{numero_info['numero']}`\n🌐 {servico}\n💰 R$ {preco:.2f}\n💵 Saldo: R$ {usuario['saldo']:.2f}",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )

            # Agendar verificação automática
            context.job_queue.run_repeating(
                verificar_sms_auto,
                interval=10,
                first=10,
                data={"user_id": user.id, "activation_id": numero_info['activation_id'], "chat_id": query.message.chat_id},
                name=f"check_{numero_info['activation_id']}"
            )
        else:
            await query.edit_message_text(
                f"❌ *Indisponível*\n\nNão há números para {servico}.",
                parse_mode="Markdown"
            )

        return ConversationHandler.END

async def verificar_sms_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("🔄 Verificando...")

    if query.data.startswith("ver_"):
        activation_id = query.data.split("_")[1]
        codigo = obter_codigo_sms(activation_id)

        if codigo and codigo != "AGUARDANDO":
            await query.edit_message_text(
                f"✅ *SMS Recebido!*\n\n📨 `{codigo}`",
                parse_mode="Markdown"
            )

            jobs = context.job_queue.get_jobs_by_name(f"check_{activation_id}")
            for job in jobs:
                job.schedule_removal()
        else:
            await query.answer("⏳ Aguarde...", show_alert=True)

    elif query.data.startswith("can_"):
        activation_id = query.data.split("_")[1]
        if cancelar_numero_sms(activation_id):
            user = query.from_user
            categoria = context.user_data.get('categoria', 'basico')
            preco = PRECO_CATEGORIAS[categoria]["preco"]
            reembolso = preco * 0.5
            atualizar_saldo(user.id, reembolso)

            await query.edit_message_text(
                f"✅ *Cancelado*\n\nReembolso: R$ {reembolso:.2f}",
                parse_mode="Markdown"
            )

async def verificar_sms_auto(context: ContextTypes.DEFAULT_TYPE):
    job_data = context.job.data
    activation_id = job_data['activation_id']
    chat_id = job_data['chat_id']

    codigo = obter_codigo_sms(activation_id)

    if codigo and codigo != "AGUARDANDO":
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🎉 *SMS Recebido!*\n\n📨 `{codigo}`",
            parse_mode="Markdown"
        )
        context.job.schedule_removal()

async def historico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    usuario = get_usuario(user.id)

    if not usuario['numeros_ativos']:
        await update.message.reply_text("📋 Histórico vazio. Use /comprar!")
        return

    mensagem = "📋 *Histórico*\n\n"
    for idx, compra in enumerate(usuario['numeros_ativos'][-10:], 1):
        data = datetime.fromisoformat(compra['data']).strftime("%d/%m %H:%M")
        mensagem += f"{idx}. {compra['servico']} - {compra['numero']} ({data})\n"

    await update.message.reply_text(mensagem, parse_mode="Markdown")

async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 *Ajuda*\n\n/start - Iniciar\n/comprar - Comprar\n/depositar - Adicionar\n/saldo - Ver saldo\n/historico - Histórico",
        parse_mode="Markdown"
    )

# ============== MAIN ==============
def main():
    logger.info("🚀 Iniciando bot...")

    # Criar aplicação (SEM usar Updater!)
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("saldo", saldo))
    app.add_handler(CommandHandler("depositar", depositar))
    app.add_handler(CommandHandler("historico", historico))
    app.add_handler(CommandHandler("ajuda", ajuda))

    # Conversation handler
    conv = ConversationHandler(
        entry_points=[CommandHandler("comprar", comprar)],
        states={
            ESCOLHER_CATEGORIA: [CallbackQueryHandler(escolher_categoria)],
            ESCOLHER_SERVICO: [CallbackQueryHandler(escolher_servico)],
        },
        fallbacks=[],
    )
    app.add_handler(conv)

    # Callbacks
    app.add_handler(CallbackQueryHandler(processar_deposito, pattern="^dep_"))
    app.add_handler(CallbackQueryHandler(verificar_sms_callback, pattern="^ver_"))
    app.add_handler(CallbackQueryHandler(verificar_sms_callback, pattern="^can_"))

    logger.info("✅ Bot configurado!")
    logger.info("🔄 Iniciando polling...")

    # Usar run_polling ao invés de start_polling (que usa Updater)
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

    logger.info("🛑 Bot finalizado.")

if __name__ == "__main__":
    main()
