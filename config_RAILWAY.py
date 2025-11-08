"""
Configurações do Bot - RAILWAY OPTIMIZED
Não usa arquivo .env - carrega direto das variáveis de ambiente
"""

import os
import logging

logger = logging.getLogger(__name__)

# ==========================================================================
# CARREGAR VARIÁVEIS DIRETO DO AMBIENTE (SEM .env)
# ==========================================================================

# Telegram
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

if not TELEGRAM_BOT_TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN não configurado!")
    raise ValueError("TELEGRAM_BOT_TOKEN é obrigatório")

# Admin IDs
ADMIN_IDS_STR = os.environ.get("ADMIN_IDS", "")
try:
    ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(",") if id.strip()]
except:
    ADMIN_IDS = []
    logger.warning("⚠️ ADMIN_IDS não configurado ou inválido")

# SMS Activate
SMS_ACTIVATE_API_KEY = os.environ.get("SMS_ACTIVATE_API_KEY", "")
SMS_ACTIVATE_BASE_URL = "https://api.sms-activate.org/stubs/handler_api.php"

# Pluggy
PLUGGY_CLIENT_ID = os.environ.get("PLUGGY_CLIENT_ID", "")
PLUGGY_API_KEY = os.environ.get("PLUGGY_API_KEY", "")
PLUGGY_BASE_URL = "https://api.pluggy.ai"

# Apex Seguidores
APEX_API_KEY = os.environ.get("APEX_API_KEY", "")
APEX_BASE_URL = "https://apexseguidores.com/api/v2"

# Referral
try:
    REFERRAL_BONUS = float(os.environ.get("REFERRAL_BONUS", "5.0"))
    REFERRAL_PERCENTAGE = float(os.environ.get("REFERRAL_PERCENTAGE", "5.0"))
except:
    REFERRAL_BONUS = 5.0
    REFERRAL_PERCENTAGE = 5.0

# Database
DATABASE_PATH = os.environ.get("DATABASE_PATH", "bot_database.db")

# Preços SMS
SMS_PRICES = {
    "br": 5.0,
    "us": 7.0,
    "ru": 4.0,
    "cn": 6.0,
    "uk": 7.5,
    "de": 7.5
}

# Service Categories (para compatibilidade)
SERVICE_CATEGORIES = {
    "popular": {
        "telegram": "Telegram",
        "whatsapp": "WhatsApp",
        "instagram": "Instagram",
        "facebook": "Facebook"
    },
    "social": {
        "twitter": "Twitter/X",
        "tiktok": "TikTok",
        "snapchat": "Snapchat"
    }
}

# Config class (para compatibilidade com código antigo)
class Config:
    TELEGRAM_BOT_TOKEN = TELEGRAM_BOT_TOKEN
    ADMIN_IDS = ADMIN_IDS
    SMS_ACTIVATE_API_KEY = SMS_ACTIVATE_API_KEY
    PLUGGY_CLIENT_ID = PLUGGY_CLIENT_ID
    PLUGGY_API_KEY = PLUGGY_API_KEY
    APEX_API_KEY = APEX_API_KEY
    REFERRAL_BONUS = REFERRAL_BONUS
    REFERRAL_PERCENTAGE = REFERRAL_PERCENTAGE
    DATABASE_PATH = DATABASE_PATH

# Log das configurações
logger.info("✅ Configurações carregadas do ambiente")
logger.info(f"📱 Bot Token: {TELEGRAM_BOT_TOKEN[:15]}...")
logger.info(f"👥 Admins configurados: {len(ADMIN_IDS)}")
logger.info(f"🔑 SMS Activate: {'✅' if SMS_ACTIVATE_API_KEY else '❌'}")
logger.info(f"💳 Pluggy: {'✅' if PLUGGY_API_KEY else '❌'}")
logger.info(f"📊 Apex: {'✅' if APEX_API_KEY else '❌'}")

print("✅ Config carregado com sucesso (Railway mode)")
