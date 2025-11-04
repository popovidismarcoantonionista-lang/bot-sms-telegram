#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot de Vendas de SMS para Telegram
Deploy: Render.com 24/7
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
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============== CONFIGURAÇÕES (Variáveis de Ambiente) ==============
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7958563749:AAGUWtp2ISNcegnOHAr1Hfqu_dpigJPJR8s")
PLUGGY_CLIENT_ID = os.getenv("PLUGGY_CLIENT_ID", "3d15ed55-b74a-4b7c-8bcc-430e80cf01ab")
PLUGGY_CLIENT_SECRET = os.getenv("PLUGGY_CLIENT_SECRET", "ccef002e-7935-452b-ace8-dde1db125e81")
PLUGGY_BASE_URL = "https://api.pluggy.ai"
SMS_ACTIVATE_API_KEY = os.getenv("SMS_ACTIVATE_API_KEY", "58f78469017177b5defd637edA3983d1")
SMS_ACTIVATE_BASE_URL = "https://api.sms-activate.org/stubs/handler_api.php"

# Configurações de preços
PRECO_CATEGORIAS = {
    "basico": {"preco": 0.60, "servicos": ["WhatsApp", "Telegram", "Discord"]},
    "padrao": {"preco": 1.00, "servicos": ["Instagram", "Facebook", "Twitter", "TikTok"]},
    "premium": {"preco": 2.50, "servicos": ["Google", "Microsoft", "Amazon", "PayPal"]}
}
DEPOSITO_MINIMO = 1.00

# Estados da conversa
ESCOLHER_CATEGORIA, ESCOLHER_SERVICO, AGUARDAR_DEPOSITO = range(3)

# ============== BANCO DE DADOS ==============
DATABASE_FILE = "database.json"

def carregar_database():
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def salvar_database(db):
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

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

# ============== INTEGRAÇÃO SMS ACTIVATE ==============
def obter_numero_sms(servico: str, pais: str = "br") -> Optional[Dict]:
    try:
        servico_map = {
            "WhatsApp": "wa", "Telegram": "tg", "Discord": "ds",
            "Instagram": "ig", "Facebook": "fb", "Twitter": "tw",
            "TikTok": "tt", "Google": "go", "Microsoft": "mm",
            "Amazon": "am", "PayPal": "pp"
        }

        codigo_servico = servico_map.get(servico, "wa")

        response = requests.get(
            SMS_ACTIVATE_BASE_URL,
            params={
                "api_key": SMS_ACTIVATE_API_KEY,
                "action": "getNumber",
                "service": codigo_servico,
                "country": 132  # Brasil
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
        logger.error(f"Exceção ao obter número: {e}")
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
        logger.error(f"Erro ao obter código: {e}")
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
    except Exception as e:
        logger.error(f"Erro ao cancelar: {e}")
        return False

# ============== COMANDOS DO BOT ==============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    usuario = get_usuario(user.id)

    mensagem = f"""
🎉 *Bem-vindo ao Bot de SMS!* 🎉

Olá {user.first_name}! Compre números SMS para verificação de contas.

💰 *Seu Saldo*: R$ {usuario['saldo']:.2f}

📱 *Preços*:
• Básico (R$ 0,60): WhatsApp, Telegram, Discord
• Padrão (R$ 1,00): Instagram, Facebook, Twitter, TikTok  
• Premium (R$ 2,50): Google, Microsoft, Amazon, PayPal

⚡ *Comandos*:
/comprar - Comprar número SMS
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
        f"💰 *Saldo*: R$ {usuario['saldo']:.2f}\n\nUse /depositar para adicionar saldo.",
        parse_mode="Markdown"
    )

async def depositar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("R$ 5,00", callback_data="deposito_5")],
        [InlineKeyboardButton("R$ 10,00", callback_data="deposito_10")],
        [InlineKeyboardButton("R$ 20,00", callback_data="deposito_20")],
        [InlineKeyboardButton("R$ 50,00", callback_data="deposito_50")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"💳 *Adicionar Saldo*\n\nSelecione o valor (mínimo R$ {DEPOSITO_MINIMO:.2f}):",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def processar_deposito(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    data = query.data

    if data.startswith("deposito_"):
        valor = float(data.split("_")[1])

        # Por enquanto, crédito manual (você pode integrar Pluggy depois)
        mensagem = f"""
✅ *Instruções de Pagamento*

Valor: R$ {valor:.2f}

📱 *PIX*: Envie para a chave abaixo
`seu-pix@email.com`

Após pagar, envie o comprovante para @seu_usuario

⏰ Crédito em até 5 minutos.
        """

        await query.edit_message_text(mensagem, parse_mode="Markdown")

async def comprar_numero(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📱 Básico (R$ 0,60)", callback_data="categoria_basico")],
        [InlineKeyboardButton("📱 Padrão (R$ 1,00)", callback_data="categoria_padrao")],
        [InlineKeyboardButton("📱 Premium (R$ 2,50)", callback_data="categoria_premium")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    user = update.effective_user
    usuario = get_usuario(user.id)

    await update.message.reply_text(
        f"🛒 *Comprar Número*\n\nSaldo: R$ {usuario['saldo']:.2f}\n\nEscolha:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def escolher_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("categoria_"):
        categoria = data.split("_")[1]
        context.user_data['categoria'] = categoria

        servicos = PRECO_CATEGORIAS[categoria]["servicos"]
        preco = PRECO_CATEGORIAS[categoria]["preco"]

        keyboard = [[InlineKeyboardButton(f"📱 {s}", callback_data=f"servico_{s}")] for s in servicos]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"📱 *{categoria.title()}* - R$ {preco:.2f}\n\nEscolha o serviço:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

        return ESCOLHER_SERVICO

async def escolher_servico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    usuario = get_usuario(user.id)
    data = query.data

    if data.startswith("servico_"):
        servico = data.split("_")[1]
        categoria = context.user_data.get('categoria', 'basico')
        preco = PRECO_CATEGORIAS[categoria]["preco"]

        if usuario['saldo'] < preco:
            await query.edit_message_text(
                f"❌ *Saldo Insuficiente*\n\nPreço: R$ {preco:.2f}\nSeu saldo: R$ {usuario['saldo']:.2f}\n\nUse /depositar",
                parse_mode="Markdown"
            )
            return ConversationHandler.END

        await query.edit_message_text("⏳ Buscando número disponível...")

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
                [InlineKeyboardButton("🔄 Verificar SMS", callback_data=f"verificar_{numero_info['activation_id']}")],
                [InlineKeyboardButton("❌ Cancelar", callback_data=f"cancelar_{numero_info['activation_id']}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"✅ *Número Adquirido!*\n\n📱 `{numero_info['numero']}`\n🌐 {servico}\n💰 R$ {preco:.2f}\n💵 Saldo: R$ {usuario['saldo']:.2f}\n\n⚠️ Use no {servico} e clique em 'Verificar SMS'",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )

            context.job_queue.run_repeating(
                verificar_sms_auto,
                interval=10,
                first=10,
                data={"user_id": user.id, "activation_id": numero_info['activation_id'], "chat_id": query.message.chat_id},
                name=f"check_{numero_info['activation_id']}"
            )
        else:
            await query.edit_message_text(
                f"❌ *Número Indisponível*\n\nNão há números para {servico}.\n\nTente outro serviço.",
                parse_mode="Markdown"
            )

        return ConversationHandler.END

async def verificar_sms_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("🔄 Verificando...")

    data = query.data

    if data.startswith("verificar_"):
        activation_id = data.split("_")[1]
        codigo = obter_codigo_sms(activation_id)

        if codigo and codigo != "AGUARDANDO":
            await query.edit_message_text(
                f"✅ *SMS Recebido!*\n\n📨 `{codigo}`\n\nUse este código!",
                parse_mode="Markdown"
            )
            jobs = context.job_queue.get_jobs_by_name(f"check_{activation_id}")
            for job in jobs:
                job.schedule_removal()
        else:
            await query.answer("⏳ SMS ainda não chegou.", show_alert=True)

    elif data.startswith("cancelar_"):
        activation_id = data.split("_")[1]
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
            jobs = context.job_queue.get_jobs_by_name(f"check_{activation_id}")
            for job in jobs:
                job.schedule_removal()

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
        "📚 *Ajuda*\n\n/start - Iniciar\n/comprar - Comprar número\n/depositar - Adicionar saldo\n/saldo - Ver saldo\n/historico - Ver compras",
        parse_mode="Markdown"
    )

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("saldo", saldo))
    application.add_handler(CommandHandler("depositar", depositar))
    application.add_handler(CommandHandler("historico", historico))
    application.add_handler(CommandHandler("ajuda", ajuda))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("comprar", comprar_numero)],
        states={
            ESCOLHER_CATEGORIA: [CallbackQueryHandler(escolher_categoria)],
            ESCOLHER_SERVICO: [CallbackQueryHandler(escolher_servico)],
        },
        fallbacks=[],
    )
    application.add_handler(conv_handler)

    application.add_handler(CallbackQueryHandler(processar_deposito, pattern="^deposito_"))
    application.add_handler(CallbackQueryHandler(verificar_sms_callback, pattern="^verificar_"))
    application.add_handler(CallbackQueryHandler(verificar_sms_callback, pattern="^cancelar_"))

    logger.info("🚀 Bot iniciado!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
