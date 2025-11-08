import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
from datetime import datetime

from config import Config, SERVICE_CATEGORIES
from database import db, User, Transaction, SMSPurchase
from pluggy_checker import pluggy_checker
from sms_activate import sms_activate
from apex_seguidores import apex_api

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO if not Config.DEBUG else logging.DEBUG
)
logger = logging.getLogger(__name__)

# Validate configuration
Config.validate()

# Initialize database
db.init_db()

class SMSBot:
    def __init__(self):
        self.app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        # Configure connection timeouts
        from telegram.request import HTTPXRequest
        request = HTTPXRequest(
            connection_pool_size=10,
            connect_timeout=20.0,
            read_timeout=20.0,
            write_timeout=20.0,
            pool_timeout=20.0
        )
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("saldo", self.saldo_command))
        self.app.add_handler(CommandHandler("depositar", self.depositar_command))
        self.app.add_handler(CommandHandler("comprar", self.comprar_command))
        self.app.add_handler(CommandHandler("historico", self.historico_command))
        self.app.add_handler(CommandHandler("ajuda", self.ajuda_command))
        self.app.add_handler(CommandHandler("social", self.social_command))

        if Config.TELEGRAM_ADMIN_ID:
            self.app.add_handler(CommandHandler("admin", self.admin_command))


        # Message handler for Apex links
        from telegram.ext import MessageHandler, filters
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_text_message
        ))

        # Callback handlers
        self.app.add_handler(CallbackQueryHandler(self.button_callback))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user

        # Create or get user in database
        db_user = db.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name
        )

        welcome_text = f"""
🎉 *Bem-vindo ao Bot SMS Temporário!*

Olá {user.first_name}! 👋

Aqui você pode comprar números temporários para receber SMS de verificação de diversos serviços.

💰 *Seu Saldo Atual:* R$ {db_user.balance:.2f}

📱 *Como funciona:*
1. Faça um depósito via PIX
2. Escolha o serviço que deseja
3. Receba o número e aguarde o SMS

💵 *Preços:*
• Básico (WhatsApp, Telegram, Discord): R$ {Config.PRICE_BASIC:.2f}
• Padrão (Instagram, Facebook, Twitter, TikTok): R$ {Config.PRICE_STANDARD:.2f}
• Premium (Google, Microsoft, Amazon, PayPal): R$ {Config.PRICE_PREMIUM:.2f}

📋 *Comandos Disponíveis:*
/saldo - Ver seu saldo
/depositar - Fazer depósito via PIX
/comprar - Comprar número SMS
/historico - Ver histórico de compras
/ajuda - Obter ajuda

Pronto para começar? Use /depositar para adicionar créditos! 💳\n\n📞 Suporte: @marcodeveloper604
"""

        keyboard = [
            [InlineKeyboardButton("💰 Ver Saldo", callback_data="saldo")],
            [InlineKeyboardButton("💳 Depositar", callback_data="depositar")],
            [InlineKeyboardButton("📱 Comprar SMS", callback_data="comprar")],
            [InlineKeyboardButton("📊 Histórico", callback_data="historico")],
            [InlineKeyboardButton("📱 Redes Sociais", callback_data="social")],
            [InlineKeyboardButton("❓ Ajuda", callback_data="ajuda")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def saldo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /saldo command"""
        user = update.effective_user
        db_user = db.get_or_create_user(telegram_id=user.id)

        # Get recent transactions
        recent_trans = db.get_user_transactions(user.id, limit=5)

        trans_text = ""
        if recent_trans:
            trans_text = "\n\n📋 *Últimas Transações:*\n"
            for trans in recent_trans:
                emoji = "💰" if trans.type == "deposit" else "📱" if trans.type == "purchase" else "↩️"
                trans_text += f"{emoji} {trans.type.title()}: R$ {abs(trans.amount):.2f} - {trans.created_at.strftime('%d/%m %H:%M')}\n"

        saldo_text = f"""
💰 *Seu Saldo Atual*

Saldo disponível: *R$ {db_user.balance:.2f}*
{trans_text}

Use /depositar para adicionar créditos
Use /comprar para comprar números SMS
"""

        keyboard = [
            [InlineKeyboardButton("💳 Depositar", callback_data="depositar")],
            [InlineKeyboardButton("📱 Comprar SMS", callback_data="comprar")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            saldo_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def depositar_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /depositar command"""
        user = update.effective_user
        db_user = db.get_or_create_user(telegram_id=user.id)

        deposit_text = f"""
💳 *Depósito via PIX*

Para adicionar créditos à sua conta, siga os passos:

1️⃣ Faça um PIX para:
  🔧 *Chave:* `092.675.711-33`
  👤 *Nome: {Config.PIX_NAME}

2️⃣ *IMPORTANTE:* No campo de descrição/mensagem do PIX, coloque:
  🆔 `{db_user.unique_deposit_id}`

3️⃣ Aguarde a confirmação automática (até 2 minutos)

⚠️ *Atenção:*
• Valor mínimo: R$ 5,00
• Valor máximo: R$ 500,00
• Use EXATAMENTE o ID acima na descrição
• Sem o ID correto, não conseguimos identificar seu pagamento

💡 Após o pagamento, o saldo é creditado automaticamente!
"""

        keyboard = [[InlineKeyboardButton("✅ Já fiz o PIX", callback_data="check_deposit")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            deposit_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )