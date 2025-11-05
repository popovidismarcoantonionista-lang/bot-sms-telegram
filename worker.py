import logging
import time
import asyncio
from telegram import Bot
from telegram.constants import ParseMode

from config import Config
from database import db, Transaction
from pluggy_checker import pluggy_checker

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database
db.init_db()

class DepositWorker:
    """Background worker to check for new deposits"""

    def __init__(self):
        self.bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        self.check_interval = Config.PLUGGY_CHECK_INTERVAL

    async def check_all_pending_deposits(self):
        """Check for pending deposits for all users"""
        logger.info("Checking for new deposits...")

        try:
            # Get all users with unique deposit IDs
            session = db.get_session()
            from database import User
            users = session.query(User).all()

            for user in users:
                try:
                    # Check for transactions with this user's ID
                    transaction = pluggy_checker.find_deposit_by_description(
                        user.unique_deposit_id,
                        min_amount=1.0
                    )

                    if transaction:
                        trans_id = transaction['id']
                        amount = abs(float(transaction.get('amount', 0)))

                        # Check if already processed
                        existing = session.query(Transaction).filter_by(
                            pluggy_transaction_id=trans_id
                        ).first()

                        if not existing:
                            # Credit user
                            new_balance = db.update_user_balance(user.telegram_id, amount)
                            db.create_transaction(
                                telegram_id=user.telegram_id,
                                trans_type='deposit',
                                amount=amount,
                                description=f"Depósito PIX automático",
                                pluggy_id=trans_id
                            )

                            # Notify user
                            try:
                                await self.bot.send_message(
                                    chat_id=user.telegram_id,
                                    text=f"✅ *Depósito Confirmado!*\n\nValor: R$ {amount:.2f}\nNovo saldo: R$ {new_balance:.2f}\n\nUse /comprar para comprar números SMS!",
                                    parse_mode=ParseMode.MARKDOWN
                                )
                                logger.info(f"Processed deposit for user {user.telegram_id}: R$ {amount:.2f}")
                            except Exception as e:
                                logger.error(f"Error notifying user {user.telegram_id}: {e}")

                except Exception as e:
                    logger.error(f"Error checking deposits for user {user.telegram_id}: {e}")
                    continue

            session.close()

        except Exception as e:
            logger.error(f"Error in deposit check cycle: {e}")

    async def run(self):
        """Main worker loop"""
        logger.info(f"Starting deposit worker (check interval: {self.check_interval}s)")

        while True:
            try:
                await self.check_all_pending_deposits()
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")

            # Wait before next check
            await asyncio.sleep(self.check_interval)

if __name__ == "__main__":
    worker = DepositWorker()
    asyncio.run(worker.run())
