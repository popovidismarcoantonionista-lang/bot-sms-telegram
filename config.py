import os
from typing import Optional
from dataclasses import dataclass
import logging

@dataclass
class Config:
    """Configurações centralizadas do bot"""

    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_ADMIN_ID: int

    # Pluggy
    PLUGGY_CLIENT_ID: str
    PLUGGY_CLIENT_SECRET: str
    PLUGGY_ENVIRONMENT: str
    PLUGGY_API_URL: str
    PLUGGY_WEBHOOK_URL: str

    # SMS Activate
    SMS_ACTIVATE_API_KEY: str
    SMS_ACTIVATE_API_URL: str = "https://api.sms-activate.org/stubs/handler_api.php"

    # Database
    DATABASE_URL: str

    # Webhook
    WEBHOOK_HOST: str
    WEBHOOK_PORT: int
    WEBHOOK_SECRET: str

    # Pricing (em reais)
    PRICE_BASIC: float = 0.60
    PRICE_STANDARD: float = 1.00
    PRICE_PREMIUM: float = 2.50

    # Refund
    REFUND_PERCENTAGE: float = 0.50

    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE: int = 10

    # Logging
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False

    @classmethod
    def from_env(cls) -> "Config":
        """Carrega configurações do ambiente"""

        # Validar variáveis obrigatórias
        required_vars = [
            "TELEGRAM_BOT_TOKEN",
            "TELEGRAM_ADMIN_ID",
            "PLUGGY_CLIENT_ID",
            "PLUGGY_CLIENT_SECRET",
            "SMS_ACTIVATE_API_KEY",
            "WEBHOOK_SECRET"
        ]

        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise ValueError(
                f"Variáveis de ambiente obrigatórias não configuradas: {', '.join(missing)}\n"
                f"Copie .env.example para .env e configure as variáveis."
            )

        # Determinar URL da API Pluggy baseado no ambiente
        env = os.getenv("PLUGGY_ENVIRONMENT", "sandbox").lower()
        pluggy_api_url = (
            "https://api.pluggy.ai" if env == "production" 
            else "https://api.pluggy.ai/sandbox"
        )

        return cls(
            TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN"),
            TELEGRAM_ADMIN_ID=int(os.getenv("TELEGRAM_ADMIN_ID")),
            PLUGGY_CLIENT_ID=os.getenv("PLUGGY_CLIENT_ID"),
            PLUGGY_CLIENT_SECRET=os.getenv("PLUGGY_CLIENT_SECRET"),
            PLUGGY_ENVIRONMENT=env,
            PLUGGY_API_URL=pluggy_api_url,
            PLUGGY_WEBHOOK_URL=os.getenv("PLUGGY_WEBHOOK_URL", ""),
            SMS_ACTIVATE_API_KEY=os.getenv("SMS_ACTIVATE_API_KEY"),
            DATABASE_URL=os.getenv("DATABASE_URL", "sqlite:///bot_database.db"),
            WEBHOOK_HOST=os.getenv("WEBHOOK_HOST", "0.0.0.0"),
            WEBHOOK_PORT=int(os.getenv("WEBHOOK_PORT", "5000")),
            WEBHOOK_SECRET=os.getenv("WEBHOOK_SECRET"),
            LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
            DEBUG=os.getenv("DEBUG", "false").lower() == "true"
        )

def setup_logging(config: Config):
    """Configura sistema de logs"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )
