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
  🔧 *Chave:* `{Config.PIX_KEY}`
  👤 *Nome: {Config.PIX_NAME}

2️⃣ *IMPORTANTE:* No campo de descrição/mensagem do PIX, coloque:
  🆔 `{db_user.unique_deposit_id}`

3️⃣ Aguarde a confirmação automática (até 2 minutos)

⚠️ *Atenção:*
• Valor mínimo: R$ 5,00,00
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

    async def comprar_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /comprar command"""
        user = update.effective_user
        db_user = db.get_or_create_user(telegram_id=user.id)

        comprar_text = f"""
📱 *Comprar Número SMS*

Seu saldo: *R$ {db_user.balance:.2f}*

Escolha a categoria do serviço:

💚 *BÁSICO - R$ {Config.PRICE_BASIC:.2f}*
WhatsApp, Telegram, Discord

💙 *PADRÃO - R$ {Config.PRICE_STANDARD:.2f}*
Instagram, Facebook, Twitter, TikTok

💜 *PREMIUM - R$ {Config.PRICE_PREMIUM:.2f}*
Google, Microsoft, Amazon, PayPal
"""

        keyboard = [
            [InlineKeyboardButton(f"💚 Básico (R$ {Config.PRICE_BASIC:.2f})", callback_data="buy_basic")],
            [InlineKeyboardButton(f"💙 Padrão (R$ {Config.PRICE_STANDARD:.2f})", callback_data="buy_standard")],
            [InlineKeyboardButton(f"💜 Premium (R$ {Config.PRICE_PREMIUM:.2f})", callback_data="buy_premium")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            comprar_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def historico_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /historico command"""
        user = update.effective_user
        transactions = db.get_user_transactions(user.id, limit=20)

        if not transactions:
            await update.message.reply_text(
                "📊 *Histórico de Transações*\n\nVocê ainda não tem transações.",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        history_text = "📊 *Seu Histórico de Transações*\n\n"

        for trans in transactions:
            emoji = "💰" if trans.type == "deposit" else "📱" if trans.type == "purchase" else "↩️"
            date_str = trans.created_at.strftime("%d/%m/%Y %H:%M")

            history_text += f"{emoji} *{trans.type.title()}*\n"
            history_text += f"   Valor: R$ {abs(trans.amount):.2f}\n"
            if trans.description:
                history_text += f"   {trans.description}\n"
            history_text += f"   Data: {date_str}\n\n"

        await update.message.reply_text(history_text, parse_mode=ParseMode.MARKDOWN)

    async def ajuda_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ajuda command"""
        ajuda_text = """
❓ *Ajuda - Bot SMS Temporário*

*Como funciona?*
1. Deposite créditos via PIX
2. Escolha um serviço (WhatsApp, Instagram, etc)
3. Receba o número temporário
4. Use o número no serviço desejado
5. Aguarde o SMS de verificação
6. Clique em "Verificar SMS" para receber o código

*Perguntas Frequentes:*

*Q: Quanto tempo demora para receber o SMS?*
R: Geralmente de 1 a 5 minutos. Máximo 20 minutos.

*Q: E se o SMS não chegar?*
R: Você pode cancelar e receber 50% de reembolso.

*Q: Posso usar o mesmo número várias vezes?*
R: Não, os números são temporários e descartáveis.

*Q: Quanto tempo demora o depósito?*
R: Após fazer o PIX com o ID correto, até 2 minutos.

*Q: Quais serviços posso usar?*
R: WhatsApp, Telegram, Discord, Instagram, Facebook, Twitter, TikTok, Google, Microsoft, Amazon, PayPal e mais!

*Suporte:*
Em caso de problemas, entre em contato:\n👤 @marcodeveloper604

*Comandos:*
/start - Início
/saldo - Ver saldo
/depositar - Depositar via PIX
/comprar - Comprar número
/historico - Ver histórico
"""

        await update.message.reply_text(ajuda_text, parse_mode=ParseMode.MARKDOWN)

    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command (only for admin)"""
        user = update.effective_user

        if user.id != int(Config.TELEGRAM_ADMIN_ID):
            await update.message.reply_text("❌ Você não tem permissão para usar este comando.")
            return

        # Get statistics
        session = db.get_session()
        total_users = session.query(User).count()
        total_transactions = session.query(Transaction).count()
        total_purchases = session.query(SMSPurchase).count()

        # Calculate totals
        deposits = session.query(Transaction).filter_by(type='deposit').all()
        total_deposited = sum(t.amount for t in deposits)

        purchases = session.query(Transaction).filter_by(type='purchase').all()
        total_spent = sum(abs(t.amount) for t in purchases)

        session.close()

        admin_text = f"""
🔧 *Painel Administrativo*

👥 *Usuários:* {total_users}
💰 *Depósitos:* R$ {total_deposited:.2f}
📱 *Compras:* {total_purchases}
💸 *Gasto Total:* R$ {total_spent:.2f}
📊 *Transações:* {total_transactions}

💼 *Saldo SMS-Activate:*
Verificando...
"""

        await update.message.reply_text(admin_text, parse_mode=ParseMode.MARKDOWN)

        # Check SMS-Activate balance
        try:
            sms_balance = sms_activate.get_balance()
            if sms_balance:
                await update.message.reply_text(
                    f"💼 *Saldo SMS-Activate:* ${sms_balance:.2f}",
                    parse_mode=ParseMode.MARKDOWN
                )
        except Exception as e:
            logger.error(f"Error checking SMS balance: {e}")

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks - UPDATED WITH CONFIRM ROUTE"""
        query = update.callback_query
        await query.answer()

        user = query.from_user
        data = query.data

        # Route to appropriate handler
        if data == "saldo":
            await self.show_saldo(query, user)
        elif data == "depositar":
            await self.show_depositar(query, user)
        elif data == "comprar":
            await self.show_comprar(query, user)
        elif data == "historico":
            await self.show_historico(query, user)
        elif data == "ajuda":
            await self.show_ajuda(query, user)
        elif data == "social":
            await self.show_social_menu(query, user)
        elif data == "check_deposit":
            await self.check_deposit(query, user)
        elif data.startswith("buy_"):
            await self.process_purchase(query, user, data)
        elif data.startswith("confirm_"):  # NEW ROUTE
            await self.confirm_purchase(query, user, data)
        elif data.startswith("check_sms_"):
            await self.check_sms(query, user, data)
        elif data.startswith("cancel_"):
            await self.cancel_purchase(query, user, data)
        elif data.startswith("apex_service_"):
            # Handle Apex service selection
            service_id = data.replace("apex_service_", "")
            await self.show_apex_service_details(query, user, service_id, context)
        elif data.startswith("confirm_apex_"):
            # Handle Apex order confirmation with quantity
            await self.process_apex_order(query, user, data, context)
        elif data.startswith("apex_"):
            # Handle Apex platform selection  
            platform = data.replace("apex_", "")
            await self.show_apex_category(query, user, platform)

        elif data == "copy_pix":
            await query.answer("📋 Chave PIX copiada!", show_alert=False)
            await query.edit_message_text(
                f"🔑 *Chave PIX*\n\n"
                f"Tipo: CPF\n"
                f"Chave: `{Config.PIX_KEY}`\n"
                f"Nome: {Config.PIX_NAME}\n\n"
                f"👆 Toque na chave para copiar!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("◀️ Voltar", callback_data="depositar")
                ]])
            )
        elif data == "copy_id":
            db_user = db.get_or_create_user(telegram_id=user.id)
            await query.answer("🆔 ID copiado!", show_alert=False)
            await query.edit_message_text(
                f"🆔 *Seu ID Único*\n\n"
                f"ID: `{db_user.unique_deposit_id}`\n\n"
                f"⚠️ Cole este ID na descrição do PIX!\n\n"
                f"👆 Toque no ID para copiar!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("◀️ Voltar", callback_data="depositar")
                ]])
            )

        elif data == "start":  # NEW: Back to start
            await self.show_start_menu(query, user)

    async def show_start_menu(self, query, user):
        """Show start menu (callback version) - NEW FUNCTION"""
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
            [InlineKeyboardButton("❓ Ajuda", callback_data="ajuda")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def show_saldo(self, query, user):
        """Show balance (callback version)"""
        db_user = db.get_or_create_user(telegram_id=user.id)
        await query.edit_message_text(
            f"💰 *Seu Saldo:* R$ {db_user.balance:.2f}\n\nUse /saldo para mais detalhes.",
            parse_mode=ParseMode.MARKDOWN
        )

    async def show_depositar(self, query, user):
        """Show deposit info with complete PIX instructions"""
        db_user = db.get_or_create_user(telegram_id=user.id)

        deposit_text = f"""
💳 *Depósito via PIX*

Para adicionar créditos à sua conta:

1️⃣ Faça um PIX para:
  🔑 *Chave PIX (CPF):* `{Config.PIX_KEY}`
  👤 *Nome:* {Config.PIX_NAME}

2️⃣ *IMPORTANTE:* Na descrição do PIX, coloque:
  🆔 `{db_user.unique_deposit_id}`

3️⃣ Aguarde confirmação (até 2 minutos)

⚠️ *Atenção:*
• Valor mínimo: R$ 5,00,00
• Valor máximo: R$ 500,00
• Use EXATAMENTE o ID acima na descrição
• Sem o ID correto, não identificamos seu pagamento

💡 Seu saldo é creditado automaticamente!
"""

        keyboard = [
            [InlineKeyboardButton("✅ Já fiz o PIX", callback_data="check_deposit")],
            [InlineKeyboardButton("🔑 Copiar Chave PIX", callback_data="copy_pix")],
            [InlineKeyboardButton("🆔 Copiar meu ID", callback_data="copy_id")],
            [InlineKeyboardButton("🏠 Menu Principal", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            deposit_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    async def show_comprar(self, query, user):
        """Show purchase options (callback version)"""
        db_user = db.get_or_create_user(telegram_id=user.id)

        comprar_text = f"""
📱 *Comprar Número SMS*

Seu saldo: *R$ {db_user.balance:.2f}*

Escolha a categoria do serviço:

💚 *BÁSICO - R$ {Config.PRICE_BASIC:.2f}*
WhatsApp, Telegram, Discord

💙 *PADRÃO - R$ {Config.PRICE_STANDARD:.2f}*
Instagram, Facebook, Twitter, TikTok

💜 *PREMIUM - R$ {Config.PRICE_PREMIUM:.2f}*
Google, Microsoft, Amazon, PayPal
"""

        keyboard = [
            [InlineKeyboardButton(f"💚 Básico (R$ {Config.PRICE_BASIC:.2f})", callback_data="buy_basic")],
            [InlineKeyboardButton(f"💙 Padrão (R$ {Config.PRICE_STANDARD:.2f})", callback_data="buy_standard")],
            [InlineKeyboardButton(f"💜 Premium (R$ {Config.PRICE_PREMIUM:.2f})", callback_data="buy_premium")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            comprar_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def show_historico(self, query, user):
        """Show history (callback version)"""
        await query.edit_message_text("📊 Use /historico para ver seu histórico completo.")

    async def show_ajuda(self, query, user):
        """Show help (callback version)"""
        await query.edit_message_text("❓ Use /ajuda para ver a ajuda completa.")

    async def check_deposit(self, query, user):
        """Check if deposit was received"""
        await query.edit_message_text("🔍 Verificando depósitos... Aguarde.")

        db_user = db.get_or_create_user(telegram_id=user.id)

        try:
            # Check Pluggy for new transactions
            transaction = pluggy_checker.find_deposit_by_description(db_user.unique_deposit_id, min_amount=1.0)

            if transaction:
                amount = abs(float(transaction.get('amount', 0)))

                # Check if already processed
                existing = db.get_session().query(Transaction).filter_by(
                    pluggy_transaction_id=transaction['id']
                ).first()

                if not existing:
                    # Credit user
                    db.update_user_balance(user.id, amount)
                    db.create_transaction(
                        telegram_id=user.id,
                        trans_type='deposit',
                        amount=amount,
                        description=f"Depósito PIX",
                        pluggy_id=transaction['id']
                    )

                    await query.edit_message_text(
                        f"✅ *Depósito Confirmado!*\n\nValor: R$ {amount:.2f}\n\nSeu novo saldo: R$ {db.get_user_balance(user.id):.2f}",
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await query.edit_message_text(
                        f"ℹ️ Este depósito já foi processado.\n\nSaldo atual: R$ {db.get_user_balance(user.id):.2f}",
                        parse_mode=ParseMode.MARKDOWN
                    )
            else:
                await query.edit_message_text(
                    f"⏳ Nenhum depósito encontrado ainda.\n\nCertifique-se de usar o ID: `{db_user.unique_deposit_id}`\n\nPode levar até 2 minutos após o pagamento.",
                    parse_mode=ParseMode.MARKDOWN
                )
        except Exception as e:
            logger.error(f"Error checking deposit: {e}")
            await query.edit_message_text(
                "❌ Erro ao verificar depósito. Tente novamente em alguns instantes."
            )

    async def process_purchase(self, query, user, data):
        """Process SMS purchase - COMPLETE IMPLEMENTATION"""
        category = data.replace("buy_", "")

        if category not in SERVICE_CATEGORIES:
            await query.edit_message_text("❌ Categoria inválida.")
            return

        category_info = SERVICE_CATEGORIES[category]
        price = category_info['price']

        db_user = db.get_or_create_user(telegram_id=user.id)

        # Check balance
        if db_user.balance < price:
            await query.edit_message_text(
                f"❌ *Saldo Insuficiente*\n\n"
                f"Preço: R$ {price:.2f}\n"
                f"Seu saldo: R$ {db_user.balance:.2f}\n\n"
                f"Use /depositar para adicionar créditos.",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Show service selection
        services = category_info['services']
        names = category_info['names']

        keyboard = []
        for service, name in zip(services, names):
            keyboard.append([InlineKeyboardButton(name, callback_data=f"confirm_{category}_{service}")])

        keyboard.append([InlineKeyboardButton("⬅️ Voltar", callback_data="comprar")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"📱 *Escolha o serviço:*\n\n"
            f"Preço: R$ {price:.2f}\n"
            f"Saldo disponível: R$ {db_user.balance:.2f}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def confirm_purchase(self, query, user, data):
        """Confirm and execute SMS purchase - NEW FUNCTION"""
        # Parse callback data: confirm_category_service
        parts = data.split("_")
        if len(parts) != 3:
            await query.answer("❌ Erro no formato.", show_alert=True)
            return

        category = parts[1]
        service = parts[2]

        if category not in SERVICE_CATEGORIES:
            await query.answer("❌ Categoria inválida.", show_alert=True)
            return

        category_info = SERVICE_CATEGORIES[category]
        price = category_info['price']
        service_name = category_info['names'][category_info['services'].index(service)]

        db_user = db.get_or_create_user(telegram_id=user.id)

        # Double-check balance
        if db_user.balance < price:
            await query.edit_message_text(
                f"❌ *Saldo Insuficiente*\n\n"
                f"Seu saldo: R$ {db_user.balance:.2f}\n"
                f"Necessário: R$ {price:.2f}",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Show processing message
        await query.edit_message_text("⏳ Processando compra...\n\nBuscando número disponível...")

        try:
            # Get number from SMS-Activate
            result = sms_activate.get_number(service=service, country='0')  # 0 = Russia (cheaper)

            if not result:
                await query.edit_message_text(
                    f"❌ *Erro na Compra*\n\n"
                    f"Não há números disponíveis para {service_name} no momento.\n\n"
                    f"Tente novamente em alguns minutos ou escolha outro serviço.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return

            activation_id = result['activation_id']
            phone_number = result['phone_number']

            # Deduct balance
            db.update_user_balance(user.id, -price)

            # Create transaction
            db.create_transaction(
                telegram_id=user.id,
                trans_type='purchase',
                amount=-price,
                description=f"Compra SMS {service_name}"
            )

            # Create SMS purchase record
            db.create_sms_purchase(
                telegram_id=user.id,
                service=service,
                phone=phone_number,
                activation_id=activation_id,
                price=price
            )

            logger.info(f"SMS purchase successful: {user.id} - {service_name} - {phone_number}")

            # Success message with number and instructions
            success_text = f"""
✅ *Compra Realizada com Sucesso!*

📱 *Serviço:* {service_name}
📞 *Número:* `{phone_number}`
💰 *Preço:* R$ {price:.2f}
💳 *Novo Saldo:* R$ {db.get_user_balance(user.id):.2f}

📝 *Instruções:*
1. Use o número acima no serviço {service_name}
2. Aguarde o SMS de verificação (até 20 minutos)
3. Clique em "Verificar SMS" abaixo para receber o código

⚠️ *Importante:*
• Você tem 20 minutos para receber o SMS
• Se não receber, você pode cancelar e receber 50% de reembolso
• Após receber o código, marque como completo

*ID da Ativação:* `{activation_id}`
"""

            keyboard = [
                [InlineKeyboardButton("🔍 Verificar SMS", callback_data=f"check_sms_{activation_id}")],
                [InlineKeyboardButton("❌ Cancelar (50% reembolso)", callback_data=f"cancel_{activation_id}")],
                [InlineKeyboardButton("🏠 Menu Principal", callback_data="start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                success_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error in confirm_purchase: {e}")
            await query.edit_message_text(
                f"❌ *Erro ao processar compra*\n\n"
                f"Ocorreu um erro inesperado. Seu saldo não foi debitado.\n\n"
                f"Por favor, tente novamente ou contate @marcodeveloper604",
                parse_mode=ParseMode.MARKDOWN
            )

    async def check_sms(self, query, user, data):
        """Check SMS status"""
        activation_id = data.replace("check_sms_", "")

        await query.answer("Verificando SMS...")

        try:
            status = sms_activate.get_status(activation_id)

            if status and status != 'WAITING':
                # Update database
                db.update_sms_status(activation_id, 'received', status)

                # Complete activation
                sms_activate.complete_activation(activation_id)

                await query.edit_message_text(
                    f"✅ *SMS Recebido!*\n\nCódigo: `{status}`\n\nUse este código no serviço.",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await query.answer("⏳ Aguardando SMS... Tente novamente em alguns segundos.", show_alert=True)
        except Exception as e:
            logger.error(f"Error checking SMS: {e}")
            await query.answer("❌ Erro ao verificar SMS.", show_alert=True)

    async def cancel_purchase(self, query, user, data):
        """Cancel SMS purchase"""
        activation_id = data.replace("cancel_", "")

        try:
            # Cancel activation
            sms_activate.cancel_activation(activation_id)

            # Get purchase info
            session = db.get_session()
            purchase = session.query(SMSPurchase).filter_by(activation_id=activation_id).first()

            if purchase and purchase.status == 'pending':
                # Refund 50%
                refund = purchase.price * 0.5
                db.update_user_balance(user.id, refund)
                db.create_transaction(
                    telegram_id=user.id,
                    trans_type='refund',
                    amount=refund,
                    description=f"Reembolso 50% - {activation_id}"
                )

                # Update purchase status
                db.update_sms_status(activation_id, 'cancelled')

                await query.edit_message_text(
                    f"✅ *Compra Cancelada*\n\nReembolso: R$ {refund:.2f} (50%)\n\nNovo saldo: R$ {db.get_user_balance(user.id):.2f}",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await query.answer("❌ Não foi possível cancelar esta compra.", show_alert=True)

            session.close()
        except Exception as e:
            logger.error(f"Error canceling purchase: {e}")
            await query.answer("❌ Erro ao cancelar compra.", show_alert=True)


    async def social_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /social command - Apex Seguidores services"""
        user = update.effective_user
        db_user = db.get_or_create_user(telegram_id=user.id)

        social_text = f"""
📱 *Serviços de Redes Sociais*

Seu saldo: *R$ {db_user.balance:.2f}*

Compre seguidores, curtidas, views e mais!

Escolha a rede social:

📸 *Instagram* - Seguidores, Curtidas, Comentários
🎵 *TikTok* - Seguidores, Curtidas, Views
▶️ *YouTube* - Inscritos, Views, Curtidas
🐦 *Twitter* - Seguidores, Retweets
📘 *Facebook* - Curtidas de página

💡 *Como funciona:*
1. Escolha a rede social
2. Escolha o tipo de serviço
3. Cole o link do perfil/post
4. Digite a quantidade
5. Confirme e pronto!

⚠️ Entrega: De instantâneo a 24h
"""

        keyboard = [
            [InlineKeyboardButton("📸 Instagram", callback_data="apex_instagram")],
            [InlineKeyboardButton("🎵 TikTok", callback_data="apex_tiktok")],
            [InlineKeyboardButton("▶️ YouTube", callback_data="apex_youtube")],
            [InlineKeyboardButton("🐦 Twitter", callback_data="apex_twitter")],
            [InlineKeyboardButton("📘 Facebook", callback_data="apex_facebook")],
            [InlineKeyboardButton("🏠 Menu Principal", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            social_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def show_social_menu(self, query, user):
        """Show social services menu (callback version)"""
        db_user = db.get_or_create_user(telegram_id=user.id)

        social_text = f"""
📱 *Serviços de Redes Sociais*

Seu saldo: *R$ {db_user.balance:.2f}*

Escolha a rede social:
"""

        keyboard = [
            [InlineKeyboardButton("📸 Instagram", callback_data="apex_instagram")],
            [InlineKeyboardButton("🎵 TikTok", callback_data="apex_tiktok")],
            [InlineKeyboardButton("▶️ YouTube", callback_data="apex_youtube")],
            [InlineKeyboardButton("🐦 Twitter", callback_data="apex_twitter")],
            [InlineKeyboardButton("📘 Facebook", callback_data="apex_facebook")],
            [InlineKeyboardButton("◀️ Voltar", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            social_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def show_apex_category(self, query, user, platform):
        """Show services for a specific platform"""
        await query.edit_message_text(f"🔍 Carregando serviços de {platform.title()}...")

        db_user = db.get_or_create_user(telegram_id=user.id)

        try:
            # Get services from Apex API
            services = apex_api.get_services_by_category(platform)

            if not services:
                await query.edit_message_text(
                    f"❌ *Erro ao carregar serviços*\n\n"
                    f"Não foi possível conectar à Apex Seguidores.\n"
                    f"Verifique se a API Key está configurada.\n\n"
                    f"Contato: @marcodeveloper604",
                    parse_mode=ParseMode.MARKDOWN
                )
                return

            # Show top services (first 10)
            text = f"""
📱 *{platform.title()} - Serviços Disponíveis*

Seu saldo: R$ {db_user.balance:.2f}

Escolha o serviço:
"""

            keyboard = []
            for i, service in enumerate(services[:10]):
                service_id = service.get('service')
                name = service.get('name', 'N/A')[:40]  # Limit name length
                rate = float(service.get('rate', 0))

                # Format button text
                button_text = f"{name} - R$ {rate:.2f}/1k"
                keyboard.append([
                    InlineKeyboardButton(
                        button_text,
                        callback_data=f"apex_service_{service_id}"
                    )
                ])

            keyboard.append([InlineKeyboardButton("◀️ Voltar", callback_data="social")])
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error loading Apex services: {e}")
            await query.edit_message_text(
                f"❌ Erro ao carregar serviços.\n\n"
                f"Tente novamente ou contate @marcodeveloper604",
                parse_mode=ParseMode.MARKDOWN
            )

    async def show_apex_service_details(self, query, user, service_id, context):
        """Show details and quantity options for a specific Apex service"""
        await query.edit_message_text("⏳ Carregando detalhes...")

        db_user = db.get_or_create_user(telegram_id=user.id)

        try:
            # Get all services to find this one
            services = apex_api.get_services()

            if not services:
                await query.edit_message_text(
                    "❌ *Erro ao conectar*\n\nNão foi possível carregar serviços da Apex.\nTente novamente em alguns instantes.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return

            # Find service by ID
            service = next((s for s in services if str(s.get('service')) == str(service_id)), None)

            if not service:
                await query.answer("❌ Serviço não encontrado", show_alert=True)
                return

            name = service.get('name')
            rate = float(service.get('rate', 0))
            min_qty = int(service.get('min', 0))
            max_qty = int(service.get('max', 0))

            text = f"""
📦 *{name}*

💰 *Preço:* R$ {rate:.2f} por 1000

📊 *Limites:*
• Mínimo: {min_qty}
• Máximo: {max_qty:,}

💡 *Exemplos de preço:*
• 100 = R$ {(rate/1000)*100:.2f}
• 500 = R$ {(rate/1000)*500:.2f}
• 1000 = R$ {rate:.2f}
• 5000 = R$ {(rate/1000)*5000:.2f}

📱 *Seu saldo:* R$ {db_user.balance:.2f}

Escolha a quantidade desejada:
"""

            # Create quantity buttons
            keyboard = [
                [InlineKeyboardButton("100", callback_data=f"confirm_apex_{service_id}_100")],
                [InlineKeyboardButton("500", callback_data=f"confirm_apex_{service_id}_500")],
                [InlineKeyboardButton("1000", callback_data=f"confirm_apex_{service_id}_1000")],
                [InlineKeyboardButton("5000", callback_data=f"confirm_apex_{service_id}_5000")],
                [InlineKeyboardButton("◀️ Voltar", callback_data="social")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error showing Apex service details: {e}")
            await query.edit_message_text(
                f"❌ Erro ao carregar detalhes.\n\nTente novamente ou contate @marcodevelo per604",
                parse_mode=ParseMode.MARKDOWN
            )


    async def process_apex_order(self, query, user, data, context):
        """Process complete Apex social media order"""
        # Parse: confirm_apex_{service_id}_{quantity}
        parts = data.replace("confirm_apex_", "").split("_")

        if len(parts) != 2:
            await query.answer("❌ Erro no formato", show_alert=True)
            return

        service_id = parts[0]
        try:
            quantity = int(parts[1])
        except ValueError:
            await query.answer("❌ Quantidade inválida", show_alert=True)
            return

        db_user = db.get_or_create_user(telegram_id=user.id)

        await query.edit_message_text("⏳ Processando pedido...\n\nAguarde...")

        try:
            # Get service details
            services = apex_api.get_services()
            service = next((s for s in services if str(s.get('service')) == str(service_id)), None)

            if not service:
                await query.edit_message_text("❌ Serviço não encontrado.")
                return

            name = service.get('name')
            rate = float(service.get('rate', 0))
            min_qty = int(service.get('min', 0))
            max_qty = int(service.get('max', 0))

            # Calculate price
            price = (rate / 1000) * quantity

            # Validate quantity
            if quantity < min_qty or quantity > max_qty:
                await query.edit_message_text(
                    f"❌ *Quantidade Inválida*\n\n"
                    f"Mínimo: {min_qty}\n"
                    f"Máximo: {max_qty:,}\n"
                    f"Você escolheu: {quantity}",
                    parse_mode=ParseMode.MARKDOWN
                )
                return

            # Check balance
            if db_user.balance < price:
                await query.edit_message_text(
                    f"❌ *Saldo Insuficiente*\n\n"
                    f"Preço: R$ {price:.2f}\n"
                    f"Seu saldo: R$ {db_user.balance:.2f}\n\n"
                    f"Use /depositar para adicionar créditos.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return

            # Ask for profile link
            await query.edit_message_text(
                f"📱 *{name}*\n\n"
                f"Quantidade: *{quantity}*\n"
                f"Preço total: *R$ {price:.2f}*\n\n"
                f"📝 *Envie o link do perfil ou post:*\n"
                f"Exemplo: https://instagram.com/seuuser\n"
                f"ou https://tiktok.com/@seuuser",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("❌ Cancelar", callback_data="social")
                ]])
            )

            # Store order info in context
            context.user_data['apex_pending_order'] = {
                'service_id': service_id,
                'service_name': name,
                'quantity': quantity,
                'price': price,
                'rate': rate
            }
            context.user_data['waiting_for_apex_link'] = True

        except Exception as e:
            logger.error(f"Error processing Apex order: {e}")
            await query.edit_message_text(
                f"❌ *Erro ao processar pedido*\n\n"
                f"Ocorreu um erro inesperado.\n"
                f"Por favor, tente novamente ou contate @marcodevelo per604",
                parse_mode=ParseMode.MARKDOWN
            )


    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages for Apex link input"""
        user = update.effective_user
        message_text = update.message.text.strip()

        # Check if waiting for Apex link
        if context.user_data.get('waiting_for_apex_link'):
            await self.process_apex_link(update, context, message_text)


    async def process_apex_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE, link: str):
        """Process Apex order with provided link"""
        user = update.effective_user
        order_info = context.user_data.get('apex_pending_order')

        if not order_info:
            await update.message.reply_text("❌ Erro: Pedido não encontrado. Tente novamente.")
            context.user_data['waiting_for_apex_link'] = False
            return

        db_user = db.get_or_create_user(telegram_id=user.id)

        # Validate link format (basic check)
        if not ('http://' in link or 'https://' in link or '@' in link):
            await update.message.reply_text(
                "❌ Link inválido!\n\n"
                "Envie um link válido, por exemplo:\n"
                "• https://instagram.com/seuuser\n"
                "• https://tiktok.com/@seuuser\n"
                "• @seuuser"
            )
            return

        service_id = order_info['service_id']
        service_name = order_info['service_name']
        quantity = order_info['quantity']
        price = order_info['price']

        # Double-check balance
        if db_user.balance < price:
            await update.message.reply_text(
                f"❌ *Saldo Insuficiente*\n\n"
                f"Preço: R$ {price:.2f}\n"
                f"Seu saldo: R$ {db_user.balance:.2f}",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data['waiting_for_apex_link'] = False
            return

        await update.message.reply_text("⏳ Criando pedido na Apex Seguidores...\n\nAguarde...")

        try:
            # Create order via Apex API
            order_result = apex_api.create_order(
                service_id=int(service_id),
                link=link,
                quantity=quantity
            )

            if not order_result:
                await update.message.reply_text(
                    "❌ *Erro ao criar pedido*\n\n"
                    "Não foi possível criar o pedido na Apex.\n"
                    "Verifique se o link está correto e tente novamente.",
                    parse_mode=ParseMode.MARKDOWN
                )
                context.user_data['waiting_for_apex_link'] = False
                return

            order_id = order_result.get('order_id')

            # Deduct balance
            db.update_user_balance(user.id, -price)

            # Create transaction
            db.create_transaction(
                telegram_id=user.id,
                trans_type='purchase',
                amount=-price,
                description=f"Apex - {service_name} ({quantity})"
            )

            logger.info(f"Apex order created: {user.id} - {service_name} - {quantity} - Order#{order_id}")

            # Success message
            success_text = f"""
✅ *Pedido Criado com Sucesso!*

📦 *Serviço:* {service_name}
🔢 *Quantidade:* {quantity}
🔗 *Link:* `{link}`
💰 *Valor:* R$ {price:.2f}
💳 *Novo Saldo:* R$ {db.get_user_balance(user.id):.2f}

🆔 *ID do Pedido:* `{order_id}`

⏱️ *Entrega:* De instantâneo a 24h

📊 *Status:* {order_result.get('status', 'Pending')}

💡 O pedido já está em processamento pela Apex Seguidores!
"""

            keyboard = [[InlineKeyboardButton("🏠 Menu Principal", callback_data="start")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                success_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )

            # Clear context
            context.user_data['waiting_for_apex_link'] = False
            context.user_data.pop('apex_pending_order', None)

        except Exception as e:
            logger.error(f"Error creating Apex order: {e}")
            await update.message.reply_text(
                f"❌ *Erro ao criar pedido*\n\n"
                f"Ocorreu um erro inesperado. Seu saldo não foi debitado.\n\n"
                f"Por favor, tente novamente ou contate @marcodevelo per604",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data['waiting_for_apex_link'] = False
            context.user_data.pop('apex_pending_order', None)

    def run(self):
        """Start the bot with retry logic"""
        import time
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Starting bot... (attempt {attempt + 1}/{max_retries})")
                self.app.run_polling(allowed_updates=Update.ALL_TYPES)
                break  # Success
            except Exception as e:
                logger.error(f"Error starting bot (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error("Max retries reached. Exiting.")
                    raise
        """Start the bot"""
        logger.info("Starting bot...")

if __name__ == "__main__":
    bot = SMSBot()
    bot.run()