#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import requests
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
TOKEN = os.getenv("TELEGRAM_TOKEN", "7958563749:AAGUWtp2ISNcegnOHAr1Hfqu_dpigJPJR8s")
SMS_KEY = os.getenv("SMS_ACTIVATE_API_KEY", "58f78469017177b5defd637edA3983d1")
SMS_URL = "https://api.sms-activate.org/stubs/handler_api.php"

PRECOS = {
    "basico": {"preco": 0.60, "servicos": ["WhatsApp", "Telegram", "Discord"]},
    "padrao": {"preco": 1.00, "servicos": ["Instagram", "Facebook", "Twitter", "TikTok"]},
    "premium": {"preco": 2.50, "servicos": ["Google", "Microsoft", "Amazon", "PayPal"]}
}

ESCOLHER_CAT, ESCOLHER_SRV = range(2)
DB_FILE = "database.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

DB = load_db()

def get_user(uid):
    uid = str(uid)
    if uid not in DB:
        DB[uid] = {"saldo": 0.0, "compras": []}
        save_db(DB)
    return DB[uid]

def add_saldo(uid, val):
    user = get_user(uid)
    user["saldo"] += val
    DB[str(uid)] = user
    save_db(DB)

def get_numero(srv):
    try:
        map_srv = {"WhatsApp": "wa", "Telegram": "tg", "Discord": "ds", "Instagram": "ig", 
                   "Facebook": "fb", "Twitter": "tw", "TikTok": "tt", "Google": "go", 
                   "Microsoft": "mm", "Amazon": "am", "PayPal": "pp"}
        r = requests.get(SMS_URL, params={"api_key": SMS_KEY, "action": "getNumber", 
                         "service": map_srv.get(srv, "wa"), "country": 132}, timeout=10)
        if r.status_code == 200:
            parts = r.text.split(":")
            if len(parts) == 3 and parts[0] == "ACCESS_NUMBER":
                return {"id": parts[1], "num": parts[2], "srv": srv}
    except:
        pass
    return None

def get_codigo(aid):
    try:
        r = requests.get(SMS_URL, params={"api_key": SMS_KEY, "action": "getStatus", "id": aid}, timeout=10)
        if r.status_code == 200:
            parts = r.text.split(":")
            if len(parts) == 2 and parts[0] == "STATUS_OK":
                return parts[1]
            if r.text == "STATUS_WAIT_CODE":
                return "AGUARDANDO"
    except:
        pass
    return None

def cancelar(aid):
    try:
        r = requests.get(SMS_URL, params={"api_key": SMS_KEY, "action": "setStatus", "id": aid, "status": 8}, timeout=10)
        return "ACCESS_CANCEL" in r.text
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u = get_user(user.id)
    msg = f"🎉 *Bot SMS*\n\nOlá {user.first_name}!\n💰 Saldo: R$ {u['saldo']:.2f}\n\n/comprar /depositar /saldo /ajuda"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)
    await update.message.reply_text(f"💰 Saldo: R$ {u['saldo']:.2f}", parse_mode="Markdown")

async def depositar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("R$ 5", callback_data="d_5")],
          [InlineKeyboardButton("R$ 10", callback_data="d_10")],
          [InlineKeyboardButton("R$ 20", callback_data="d_20")]]
    await update.message.reply_text("💳 Escolha:", reply_markup=InlineKeyboardMarkup(kb))

async def proc_dep(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data.startswith("d_"):
        v = q.data.split("_")[1]
        await q.edit_message_text(f"✅ R$ {v}\n\nPIX: `seu-pix@email.com`\nEnvie comprovante", parse_mode="Markdown")

async def comprar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)
    kb = [[InlineKeyboardButton("R$ 0,60", callback_data="c_basico")],
          [InlineKeyboardButton("R$ 1,00", callback_data="c_padrao")],
          [InlineKeyboardButton("R$ 2,50", callback_data="c_premium")]]
    await update.message.reply_text(f"🛒 Saldo: R$ {u['saldo']:.2f}", reply_markup=InlineKeyboardMarkup(kb))

async def escolher_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data.startswith("c_"):
        cat = q.data.split("_")[1]
        context.user_data['cat'] = cat
        servs = PRECOS[cat]["servicos"]
        kb = [[InlineKeyboardButton(s, callback_data=f"s_{s}")] for s in servs]
        await q.edit_message_text(f"📱 R$ {PRECOS[cat]['preco']:.2f}", reply_markup=InlineKeyboardMarkup(kb))
        return ESCOLHER_SRV

async def escolher_srv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user = q.from_user
    u = get_user(user.id)

    if q.data.startswith("s_"):
        srv = q.data.split("_")[1]
        cat = context.user_data.get('cat', 'basico')
        preco = PRECOS[cat]["preco"]

        if u['saldo'] < preco:
            await q.edit_message_text(f"❌ Insuficiente\nR$ {preco:.2f}", parse_mode="Markdown")
            return ConversationHandler.END

        await q.edit_message_text("⏳ Buscando...")
        info = get_numero(srv)

        if info:
            add_saldo(user.id, -preco)
            u['compras'].append({"id": info['id'], "num": info['num'], "srv": srv, "preco": preco, "data": datetime.now().isoformat()})
            save_db(DB)

            kb = [[InlineKeyboardButton("🔄 Ver", callback_data=f"v_{info['id']}")],
                  [InlineKeyboardButton("❌ Cancelar", callback_data=f"x_{info['id']}")]]
            await q.edit_message_text(f"✅ `{info['num']}`\n{srv}\nR$ {preco:.2f}", 
                                     reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

            context.job_queue.run_repeating(verificar_auto, interval=10, first=10,
                                           data={"uid": user.id, "aid": info['id'], "cid": q.message.chat_id},
                                           name=f"chk_{info['id']}")
        else:
            await q.edit_message_text(f"❌ Indisponível para {srv}")

        return ConversationHandler.END

async def verificar_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer("🔄")

    if q.data.startswith("v_"):
        aid = q.data.split("_")[1]
        cod = get_codigo(aid)
        if cod and cod != "AGUARDANDO":
            await q.edit_message_text(f"✅ SMS\n📨 `{cod}`", parse_mode="Markdown")
            for j in context.job_queue.get_jobs_by_name(f"chk_{aid}"):
                j.schedule_removal()
        else:
            await q.answer("⏳", show_alert=True)

    elif q.data.startswith("x_"):
        aid = q.data.split("_")[1]
        if cancelar(aid):
            cat = context.user_data.get('cat', 'basico')
            reemb = PRECOS[cat]["preco"] * 0.5
            add_saldo(q.from_user.id, reemb)
            await q.edit_message_text(f"✅ Cancelado\nR$ {reemb:.2f}")

async def verificar_auto(context: ContextTypes.DEFAULT_TYPE):
    d = context.job.data
    cod = get_codigo(d['aid'])
    if cod and cod != "AGUARDANDO":
        await context.bot.send_message(d['cid'], f"🎉 SMS\n📨 `{cod}`", parse_mode="Markdown")
        context.job.schedule_removal()

async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📚 /start /comprar /depositar /saldo")

def main():
    logger.info("🚀 Starting...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("saldo", saldo))
    app.add_handler(CommandHandler("depositar", depositar))
    app.add_handler(CommandHandler("ajuda", ajuda))

    conv = ConversationHandler(
        entry_points=[CommandHandler("comprar", comprar)],
        states={ESCOLHER_CAT: [CallbackQueryHandler(escolher_cat)], 
                ESCOLHER_SRV: [CallbackQueryHandler(escolher_srv)]},
        fallbacks=[]
    )
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(proc_dep, pattern="^d_"))
    app.add_handler(CallbackQueryHandler(verificar_cb, pattern="^v_"))
    app.add_handler(CallbackQueryHandler(verificar_cb, pattern="^x_"))

    logger.info("✅ Ready!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
