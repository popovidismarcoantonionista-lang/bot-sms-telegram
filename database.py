from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
from config import Config
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255))
    first_name = Column(String(255))
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    unique_deposit_id = Column(String(50), unique=True, index=True)

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, balance={self.balance})>"

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    telegram_id = Column(Integer, nullable=False, index=True)
    type = Column(String(50), nullable=False)  # deposit, purchase, refund
    amount = Column(Float, nullable=False)
    description = Column(Text)
    status = Column(String(50), default='pending')  # pending, completed, failed
    pluggy_transaction_id = Column(String(255), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Transaction(id={self.id}, type={self.type}, amount={self.amount})>"

class SMSPurchase(Base):
    __tablename__ = 'sms_purchases'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    telegram_id = Column(Integer, nullable=False, index=True)
    service = Column(String(50), nullable=False)
    country = Column(String(10), default='BR')
    phone_number = Column(String(50))
    activation_id = Column(String(255), index=True)
    price = Column(Float, nullable=False)
    status = Column(String(50), default='pending')  # pending, received, cancelled
    sms_code = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SMSPurchase(id={self.id}, service={self.service}, status={self.status})>"

class Database:
    def __init__(self, database_url: str = None):
        self.database_url = database_url or Config.DATABASE_URL
        self.engine = create_engine(
            self.database_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=Config.DEBUG
        )
        self.SessionLocal = scoped_session(sessionmaker(bind=self.engine))

    def init_db(self):
        """Initialize database tables"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def get_session(self):
        """Get database session"""
        return self.SessionLocal()

    def close_session(self):
        """Close database session"""
        self.SessionLocal.remove()

    # User operations
    def get_or_create_user(self, telegram_id: int, username: str = None, first_name: str = None):
        """Get existing user or create new one"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if not user:
                # Generate unique deposit ID
                unique_id = f"USR{telegram_id}"
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    unique_deposit_id=unique_id
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                logger.info(f"Created new user: {telegram_id}")
            return user
        except Exception as e:
            session.rollback()
            logger.error(f"Error getting/creating user: {e}")
            raise
        finally:
            session.close()

    def update_user_balance(self, telegram_id: int, amount: float):
        """Update user balance"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if user:
                user.balance += amount
                user.updated_at = datetime.utcnow()
                session.commit()
                logger.info(f"Updated balance for user {telegram_id}: {amount}")
                return user.balance
            return None
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating balance: {e}")
            raise
        finally:
            session.close()

    def get_user_balance(self, telegram_id: int):
        """Get user balance"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            return user.balance if user else 0.0
        finally:
            session.close()

    # Transaction operations
    def create_transaction(self, telegram_id: int, trans_type: str, amount: float, 
                          description: str = None, pluggy_id: str = None):
        """Create new transaction"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if not user:
                raise ValueError(f"User not found: {telegram_id}")

            transaction = Transaction(
                user_id=user.id,
                telegram_id=telegram_id,
                type=trans_type,
                amount=amount,
                description=description,
                pluggy_transaction_id=pluggy_id,
                status='completed'
            )
            session.add(transaction)
            session.commit()
            session.refresh(transaction)
            logger.info(f"Created transaction: {trans_type} - {amount} for user {telegram_id}")
            return transaction
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating transaction: {e}")
            raise
        finally:
            session.close()

    def get_user_transactions(self, telegram_id: int, limit: int = 10):
        """Get user transaction history"""
        session = self.get_session()
        try:
            transactions = session.query(Transaction).filter_by(
                telegram_id=telegram_id
            ).order_by(Transaction.created_at.desc()).limit(limit).all()
            return transactions
        finally:
            session.close()

    # SMS Purchase operations
    def create_sms_purchase(self, telegram_id: int, service: str, phone: str, 
                           activation_id: str, price: float):
        """Create SMS purchase record"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if not user:
                raise ValueError(f"User not found: {telegram_id}")

            purchase = SMSPurchase(
                user_id=user.id,
                telegram_id=telegram_id,
                service=service,
                phone_number=phone,
                activation_id=activation_id,
                price=price,
                status='pending'
            )
            session.add(purchase)
            session.commit()
            session.refresh(purchase)
            logger.info(f"Created SMS purchase: {activation_id} for user {telegram_id}")
            return purchase
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating SMS purchase: {e}")
            raise
        finally:
            session.close()

    def update_sms_status(self, activation_id: str, status: str, sms_code: str = None):
        """Update SMS purchase status"""
        session = self.get_session()
        try:
            purchase = session.query(SMSPurchase).filter_by(activation_id=activation_id).first()
            if purchase:
                purchase.status = status
                if sms_code:
                    purchase.sms_code = sms_code
                purchase.updated_at = datetime.utcnow()
                session.commit()
                logger.info(f"Updated SMS purchase {activation_id}: {status}")
                return purchase
            return None
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating SMS status: {e}")
            raise
        finally:
            session.close()

    def get_pending_sms_purchases(self, telegram_id: int = None):
        """Get pending SMS purchases"""
        session = self.get_session()
        try:
            query = session.query(SMSPurchase).filter_by(status='pending')
            if telegram_id:
                query = query.filter_by(telegram_id=telegram_id)
            return query.all()
        finally:
            session.close()

# Global database instance
db = Database()
