#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import requests
import time
from datetime import datetime
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Config
TOKEN = os.getenv("TELEGRAM__TOKEN", "7958563749:AAGUWtp2ISNcegnOHAr1Hfqu_dpigJPJR8s")
SMS_KEY = os.getenv("SMS_ACTIVATE_API_KEY", "58f78469017177b5defd637edA3983d1")
SMS_URL = "https://api.sms-activate.org/stubs/handler_api.php"

bot = telebot.TeleBot(TOKEN)

PRECOS = {
    "basico": {"preco": 0.60, "servicos": ["WhatsApp", "Telegram", "Discord"]},
    "padrao": {"preco": 1.00, "servicos": ["Instagram", "Facebook", "Twitter", "TikTok"]},
    "premium": {"preco": 2.50, "servicos": ["Google", "Microsoft", "Amazon", "PayPal"]}
}

DB_FILE = "database.json"
user_data = {}

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
    u = get_user(uid)
    u["saldo"] += val
    DB[str(uid)] = u
    save_db(DB)

def get_numero(srv):
    try:
        m = {"WhatsApp":"wa","Telegram":"tg","Discord":"ds","Instagram":"ig","Facebook":"fb",
             "Twitter":"tw","TikTok":"tt","Google":"go","Microsoft":"mm","Amazon":"am","PayPal":"pp"}
        r = requests.get(SMS_URL, params={"api_key":SMS_KEY,"action":"getNumber",
                        "service":m.get(srv,"wa"),"country":132}, timeout=10)
        if r.status_code == 200:
            p = r.text.split(":")
            if len(p)==3 and p[0]=="ACCESS_NUMBER":
                return {"id":p[1],"num":p[2]}
    except:
        pass
    return None

def get_codigo(aid):
    try:
        r = requests.get(SMS_URL, params={"api_key":SMS_KEY,"action":"getStatus","id":aid}, timeout=10)
        if r.status_code == 200:
            p = r.text.split(":")
            if len(p)==2 and p[0]=="STATUS_OK":
                return p[1]
            if r.text == "STATUS_WAIT_CODE":
                return "WAIT"
    except:
        pass
    return None

@bot.message_handler(commands=['start'])
def start(msg):
    u = get_user(msg.from_user.id)
    txt = f"🎉 *Bot SMS*\n\nOlá {msg.from_user.first_name}!\n💰 Saldo: R$ {u['saldo']:.2f}\n\n/comprar /depositar /saldo /ajuda"
    bot.send_message(msg.chat.id, txt, parse_mode="Markdown")

@bot.message_handler(commands=['saldo'])
def saldo(msg):
    u = get_user(msg.from_user.id)
    bot.send_message(msg.chat.id, f"💰 Saldo: R$ {u['saldo']:.2f}", parse_mode="Markdown")

@bot.message_handler(commands=['depositar'])
def depositar(msg):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("R$ 5", callback_data="d_5"))
    kb.add(InlineKeyboardButton("R$ 10", callback_data="d_10"))
    kb.add(InlineKeyboardButton("R$ 20", callback_data="d_20"))
    bot.send_message(msg.chat.id, "💳 Escolha o valor:", reply_markup=kb)

@bot.message_handler(commands=['comprar'])
def comprar(msg):
    u = get_user(msg.from_user.id)
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("R$ 0,60", callback_data="c_basico"))
    kb.add(InlineKeyboardButton("R$ 1,00", callback_data="c_padrao"))
    kb.add(InlineKeyboardButton("R$ 2,50", callback_data="c_premium"))
    bot.send_message(msg.chat.id, f"🛒 Saldo: R$ {u['saldo']:.2f}\n\nEscolha:", reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(commands=['ajuda'])
def ajuda(msg):
    bot.send_message(msg.chat.id, "📚 *Comandos*\n\n/start /comprar /depositar /saldo", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('d_'))
def proc_dep(call):
    v = call.data.split("_")[1]
    bot.edit_message_text(f"✅ R$ {v}\n\n📱 PIX: `marconista2301@gmail.com`\n\nEnvie comprovante", 
                         call.message.chat.id, call.message.id, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('c_'))
def escolher_cat(call):
    cat = call.data.split("_")[1]
    user_data[call.from_user.id] = {"cat": cat}
    servs = PRECOS[cat]["servicos"]
    kb = InlineKeyboardMarkup()
    for s in servs:
        kb.add(InlineKeyboardButton(s, callback_data=f"s_{s}"))
    bot.edit_message_text(f"📱 R$ {PRECOS[cat]['preco']:.2f}\n\nEscolha:", 
                         call.message.chat.id, call.message.id, reply_markup=kb, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('s_'))
def escolher_srv(call):
    srv = call.data.split("_")[1]
    uid = call.from_user.id
    u = get_user(uid)
    cat = user_data.get(uid, {}).get("cat", "basico")
    preco = PRECOS[cat]["preco"]

    if u['saldo'] < preco:
        bot.edit_message_text(f"❌ Saldo insuficiente\n\nPrecisa: R$ {preco:.2f}\nSeu saldo: R$ {u['saldo']:.2f}", 
                             call.message.chat.id, call.message.id, parse_mode="Markdown")
        return

    bot.edit_message_text("⏳ Buscando número...", call.message.chat.id, call.message.id)

    info = get_numero(srv)
    if info:
        add_saldo(uid, -preco)
        u['compras'].append({"id":info['id'],"num":info['num'],"srv":srv,"preco":preco,"data":datetime.now().isoformat()})
        save_db(DB)

        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("🔄 Verificar SMS", callback_data=f"v_{info['id']}"))
        kb.add(InlineKeyboardButton("❌ Cancelar", callback_data=f"x_{info['id']}_{cat}"))

        bot.edit_message_text(f"✅ *Número Adquirido!*\n\n📱 `{info['num']}`\n🌐 {srv}\n💰 R$ {preco:.2f}\n💵 Saldo: R$ {u['saldo']:.2f}\n\n⚠️ Use no {srv} e clique em Verificar", 
                             call.message.chat.id, call.message.id, reply_markup=kb, parse_mode="Markdown")
    else:
        bot.edit_message_text(f"❌ Número indisponível para {srv}\n\nTente outro serviço ou aguarde.", 
                             call.message.chat.id, call.message.id, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('v_'))
def verificar(call):
    aid = call.data.split("_")[1]
    cod = get_codigo(aid)
    if cod and cod != "WAIT":
        bot.edit_message_text(f"✅ *SMS Recebido!*\n\n📨 Código: `{cod}`\n\nUse este código!", 
                             call.message.chat.id, call.message.id, parse_mode="Markdown")
    else:
        bot.answer_callback_query(call.id, "⏳ SMS ainda não chegou. Aguarde...", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('x_'))
def cancelar(call):
    parts = call.data.split("_")
    aid = parts[1]
    cat = parts[2] if len(parts) > 2 else "basico"

    try:
        r = requests.get(SMS_URL, params={"api_key":SMS_KEY,"action":"setStatus","id":aid,"status":8}, timeout=10)
        if "ACCESS_CANCEL" in r.text:
            reemb = PRECOS[cat]["preco"] * 0.5
            add_saldo(call.from_user.id, reemb)
            bot.edit_message_text(f"✅ *Número Cancelado*\n\nReembolso: R$ {reemb:.2f}", 
                             call.message.chat.id, call.message.id, parse_mode="Markdown")
        else:
            bot.answer_callback_query(call.id, "❌ Erro ao cancelar", show_alert=True)
    except:
        bot.answer_callback_query(call.id, "❌ Erro ao cancelar", show_alert=True)

if __name__ == "__main__":
    print("🚀 Bot iniciado!")
    bot.infinity_polling()
