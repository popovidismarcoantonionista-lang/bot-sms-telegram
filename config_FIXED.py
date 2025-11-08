"""
Configurações do Bot - VERSÃO CORRIGIDA
Todas as variáveis de ambiente carregadas corretamente
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# =====================================================================
# TELEGRAM
# =====================================================================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN não configurado no .env")

# =====================================================================
# ADMINISTRADORES
# =====================================================================
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(",") if id.strip()]

if not ADMIN_IDS:
    print("⚠️  AVISO: Nenhum admin configurado")

# =====================================================================
# SMS ACTIVATE
# =====================================================================
SMS_ACTIVATE_API_KEY = os.getenv("SMS_ACTIVATE_API_KEY", "")
SMS_ACTIVATE_BASE_URL = "https://api.sms-activate.org/stubs/handler_api.php"

# =====================================================================
# PLUGGY (PAGAMENTOS)
# =====================================================================
PLUGGY_CLIENT_ID = os.getenv("PLUGGY_CLIENT_ID", "")
PLUGGY_API_KEY = os.getenv("PLUGGY_API_KEY", "")
PLUGGY_BASE_URL = "https://api.pluggy.ai"

# =====================================================================
# APEX SEGUIDORES
# =====================================================================
APEX_API_KEY = os.getenv("APEX_API_KEY", "")
APEX_BASE_URL = "https://apexseguidores.com/api/v2"

# =====================================================================
# REFERRAL SYSTEM
# =====================================================================
REFERRAL_BONUS = float(os.getenv("REFERRAL_BONUS", "5.0"))
REFERRAL_PERCENTAGE = float(os.getenv("REFERRAL_PERCENTAGE", "5.0"))

# =====================================================================
# PREÇOS
# =====================================================================
SMS_PRICES = {
    "br": 5.0,
    "us": 7.0,
    "ru": 4.0
}

# =====================================================================
# DATABASE
# =====================================================================
DATABASE_PATH = os.getenv("DATABASE_PATH", "bot_database.db")

# =====================================================================
# LOGGING
# =====================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

print("✅ Configurações carregadas com sucesso")
print(f"📱 Bot Token: {TELEGRAM_BOT_TOKEN[:10]}...")
print(f"👥 Admins: {len(ADMIN_IDS)}")
print(f"🔑 SMS Activate: {'✅' if SMS_ACTIVATE_API_KEY else '❌'}")
print(f"💳 Pluggy: {'✅' if PLUGGY_API_KEY else '❌'}")
