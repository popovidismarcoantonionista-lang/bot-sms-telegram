"""
Módulo de configuração centralizado do Bot SMS Telegram
Carrega e valida todas as variáveis de ambiente
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

class Config:
    """Configurações do bot"""

    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_ADMIN_ID = os.getenv('TELEGRAM_ADMIN_ID')

    # Pluggy
    PLUGGY_CLIENT_ID = os.getenv('PLUGGY_CLIENT_ID')
    PLUGGY_CLIENT_SECRET = os.getenv('PLUGGY_CLIENT_SECRET')
    PLUGGY_ENVIRONMENT = os.getenv('PLUGGY_ENVIRONMENT', 'production')
    PLUGGY_ITEM_ID = os.getenv('PLUGGY_ITEM_ID')
    PLUGGY_BASE_URL = 'https://api.pluggy.ai' if PLUGGY_ENVIRONMENT == 'production' else 'https://api.sandbox.pluggy.ai'

    # SMS-Activate
    SMS_ACTIVATE_API_KEY = os.getenv('SMS_ACTIVATE_API_KEY')
    SMS_ACTIVATE_BASE_URL = 'https://api.sms-activate.org/stubs/handler_api.php'

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL')

    # PIX
    PIX_KEY = os.getenv('PIX_KEY')
    PIX_NAME = os.getenv('PIX_NAME', 'Bot SMS')
    PIX_CITY = os.getenv('PIX_CITY', 'São Paulo')

    # Debug
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

    # Webhook
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', '')

    # Configurações do Bot
    CHECK_PAYMENT_INTERVAL = int(os.getenv('CHECK_PAYMENT_INTERVAL', '30'))
    MIN_DEPOSIT = float(os.getenv('MIN_DEPOSIT', '1.00'))
    MAX_DEPOSIT = float(os.getenv('MAX_DEPOSIT', '1000.00'))

    # Preços dos SMS por categoria (usados no bot.py)
    PRICE_BASIC = 0.60    # WhatsApp, Telegram, Discord
    PRICE_STANDARD = 1.00  # Instagram, Facebook, Twitter, TikTok
    PRICE_PREMIUM = 2.50   # Google, Microsoft, Amazon, PayPal

    # Preços dos SMS por categoria (dict para acesso programático)
    PRICES = {
        'basic': PRICE_BASIC,
        'standard': PRICE_STANDARD,
        'premium': PRICE_PREMIUM
    }

    # Serviços por categoria
    SERVICES = {
        'basic': ['wa', 'tg', 'ds'],
        'standard': ['ig', 'fb', 'tw', 'tk'],
        'premium': ['go', 'mm', 'am', 'pa']
    }

    @classmethod
    def validate(cls):
        """Valida se todas as variáveis obrigatórias estão configuradas"""
        required = [
            ('TELEGRAM_BOT_TOKEN', cls.TELEGRAM_BOT_TOKEN),
            ('TELEGRAM_ADMIN_ID', cls.TELEGRAM_ADMIN_ID),
            ('PLUGGY_CLIENT_ID', cls.PLUGGY_CLIENT_ID),
            ('PLUGGY_CLIENT_SECRET', cls.PLUGGY_CLIENT_SECRET),
            ('PLUGGY_ITEM_ID', cls.PLUGGY_ITEM_ID),
            ('SMS_ACTIVATE_API_KEY', cls.SMS_ACTIVATE_API_KEY),
            ('DATABASE_URL', cls.DATABASE_URL),
            ('PIX_KEY', cls.PIX_KEY),
        ]

        missing = [name for name, value in required if not value]

        if missing:
            raise ValueError(
                f"Variáveis de ambiente obrigatórias não configuradas: {', '.join(missing)}\n"
                f"Configure o arquivo .env baseado no .env.example"
            )

        return True

# Mapeamento completo: categoria -> serviços com nomes amigáveis
SERVICE_CATEGORIES = {
    'basic': {
        'price': Config.PRICE_BASIC,
        'services': ['wa', 'tg', 'ds'],
        'names': ['WhatsApp', 'Telegram', 'Discord']
    },
    'standard': {
        'price': Config.PRICE_STANDARD,
        'services': ['ig', 'fb', 'tw', 'tk'],
        'names': ['Instagram', 'Facebook', 'Twitter', 'TikTok']
    },
    'premium': {
        'price': Config.PRICE_PREMIUM,
        'services': ['go', 'mm', 'am', 'pa'],
        'names': ['Google', 'Microsoft', 'Amazon', 'PayPal']
    }
}

# Validar configurações ao importar
Config.validate()


    # Pluggy Payment API (Pix cópia e cola)
PLUGGY_API_KEY = os.getenv('PLUGGY_API_KEY')
PLUGGY_RECIPIENT_ID = os.getenv('PLUGGY_RECIPIENT_ID')
PLUGGY_WEBHOOK_URL = os.getenv('PLUGGY_WEBHOOK_URL', '')
