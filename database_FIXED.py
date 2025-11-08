"""
Database Manager - VERSÃO CORRIGIDA
Usa aiosqlite para operações async
"""

import aiosqlite
import logging
from datetime import datetime
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "bot_database.db"):
        self.db_path = db_path
        self.conn = None

    async def initialize(self):
        """Inicializa o banco de dados e cria tabelas"""
        try:
            self.conn = await aiosqlite.connect(self.db_path)
            await self._create_tables()
            logger.info("✅ Database inicializado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar database: {e}")
            raise

    async def _create_tables(self):
        """Cria todas as tabelas necessárias"""

        # Tabela de usuários
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                balance REAL DEFAULT 0.0,
                total_spent REAL DEFAULT 0.0,
                total_purchases INTEGER DEFAULT 0,
                referral_code TEXT UNIQUE,
                referred_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabela de transações
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Tabela de compras SMS
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sms_purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                phone_number TEXT NOT NULL,
                service TEXT NOT NULL,
                country TEXT NOT NULL,
                amount REAL NOT NULL,
                activation_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Tabela de cupons
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS coupons (
                code TEXT PRIMARY KEY,
                discount_percent REAL NOT NULL,
                max_uses INTEGER,
                current_uses INTEGER DEFAULT 0,
                min_purchase REAL DEFAULT 0,
                expires_at TIMESTAMP,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabela de uso de cupons
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS coupon_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                coupon_code TEXT NOT NULL,
                discount_amount REAL NOT NULL,
                used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (coupon_code) REFERENCES coupons(code)
            )
        """)

        await self.conn.commit()
        logger.info("✅ Tabelas criadas/verificadas")

    # =====================================================================
    # MÉTODOS DE USUÁRIO
    # =====================================================================

    async def create_user(self, user_id: int, username: str) -> bool:
        """Cria ou atualiza usuário"""
        try:
            await self.conn.execute("""
                INSERT OR IGNORE INTO users (user_id, username)
                VALUES (?, ?)
            """, (user_id, username))

            await self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {e}")
            return False

    async def get_balance(self, user_id: int) -> float:
        """Retorna saldo do usuário"""
        try:
            cursor = await self.conn.execute(
                "SELECT balance FROM users WHERE user_id = ?",
                (user_id,)
            )
            row = await cursor.fetchone()
            return row[0] if row else 0.0
        except Exception as e:
            logger.error(f"Erro ao buscar saldo: {e}")
            return 0.0

    async def add_balance(self, user_id: int, amount: float) -> bool:
        """Adiciona saldo ao usuário"""
        try:
            await self.conn.execute("""
                UPDATE users 
                SET balance = balance + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (amount, user_id))

            await self.conn.commit()
            logger.info(f"💰 Saldo adicionado: User {user_id} +R$ {amount:.2f}")
            return True
        except Exception as e:
            logger.error(f"Erro ao adicionar saldo: {e}")
            return False

    async def subtract_balance(self, user_id: int, amount: float) -> bool:
        """Remove saldo do usuário"""
        try:
            # Verificar se tem saldo suficiente
            current_balance = await self.get_balance(user_id)
            if current_balance < amount:
                return False

            await self.conn.execute("""
                UPDATE users 
                SET balance = balance - ?,
                    total_spent = total_spent + ?,
                    total_purchases = total_purchases + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (amount, amount, user_id))

            await self.conn.commit()
            logger.info(f"💸 Saldo debitado: User {user_id} -R$ {amount:.2f}")
            return True
        except Exception as e:
            logger.error(f"Erro ao subtrair saldo: {e}")
            return False

    async def get_user_stats(self, user_id: int) -> Dict:
        """Retorna estatísticas do usuário"""
        try:
            cursor = await self.conn.execute("""
                SELECT total_spent, total_purchases, balance, created_at
                FROM users WHERE user_id = ?
            """, (user_id,))

            row = await cursor.fetchone()
            if row:
                return {
                    "total_spent": row[0] or 0,
                    "total_purchases": row[1] or 0,
                    "balance": row[2] or 0,
                    "member_since": row[3]
                }
            return {}
        except Exception as e:
            logger.error(f"Erro ao buscar stats: {e}")
            return {}

    # =====================================================================
    # MÉTODOS DE TRANSAÇÕES
    # =====================================================================

    async def log_transaction(self, user_id: int, trans_type: str, 
                             amount: float, status: str = "completed",
                             description: str = "") -> bool:
        """Registra transação"""
        try:
            await self.conn.execute("""
                INSERT INTO transactions 
                (user_id, type, amount, status, description)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, trans_type, amount, status, description))

            await self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Erro ao registrar transação: {e}")
            return False

    async def get_user_transactions(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Retorna últimas transações do usuário"""
        try:
            cursor = await self.conn.execute("""
                SELECT type, amount, status, description, created_at
                FROM transactions
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))

            rows = await cursor.fetchall()
            return [
                {
                    "type": row[0],
                    "amount": row[1],
                    "status": row[2],
                    "description": row[3],
                    "date": row[4]
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Erro ao buscar transações: {e}")
            return []

    # =====================================================================
    # MÉTODOS DE REFERRAL
    # =====================================================================

    async def set_referral_code(self, user_id: int, code: str) -> bool:
        """Define código de referral do usuário"""
        try:
            await self.conn.execute("""
                UPDATE users 
                SET referral_code = ?
                WHERE user_id = ?
            """, (code, user_id))

            await self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Erro ao definir referral code: {e}")
            return False

    async def get_referral_code(self, user_id: int) -> Optional[str]:
        """Obtém código de referral do usuário"""
        try:
            cursor = await self.conn.execute(
                "SELECT referral_code FROM users WHERE user_id = ?",
                (user_id,)
            )
            row = await cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            logger.error(f"Erro ao buscar referral code: {e}")
            return None

    async def use_referral_code(self, new_user_id: int, code: str) -> Dict:
        """Usa código de referral"""
        try:
            # Buscar dono do código
            cursor = await self.conn.execute(
                "SELECT user_id FROM users WHERE referral_code = ?",
                (code,)
            )
            row = await cursor.fetchone()

            if not row:
                return {"success": False, "message": "Código inválido"}

            referrer_id = row[0]

            # Verificar se já usou código
            cursor = await self.conn.execute(
                "SELECT referred_by FROM users WHERE user_id = ?",
                (new_user_id,)
            )
            row = await cursor.fetchone()

            if row and row[0]:
                return {"success": False, "message": "Você já usou um código"}

            # Registrar referral
            await self.conn.execute("""
                UPDATE users 
                SET referred_by = ?
                WHERE user_id = ?
            """, (referrer_id, new_user_id))

            # Dar bônus
            await self.add_balance(new_user_id, 5.0)
            await self.add_balance(referrer_id, 10.0)

            await self.conn.commit()

            return {
                "success": True,
                "bonus": 5.0,
                "referrer_bonus": 10.0
            }
        except Exception as e:
            logger.error(f"Erro ao usar referral: {e}")
            return {"success": False, "message": "Erro ao processar"}

    async def close(self):
        """Fecha conexão com o database"""
        if self.conn:
            await self.conn.close()
            logger.info("Database fechado")
