"""
Sistema de Referral (Indicação)
Ganhe créditos indicando amigos!
"""

import logging
from database import Database
from config import REFERRAL_BONUS, REFERRAL_PERCENTAGE

logger = logging.getLogger(__name__)

class ReferralSystem:
    def __init__(self, db: Database):
        self.db = db

    async def generate_referral_code(self, user_id: int) -> str:
        """Gera código de referral único para o usuário"""
        import hashlib
        code = hashlib.md5(f"{user_id}{time.time()}".encode()).hexdigest()[:8].upper()
        await self.db.set_user_referral_code(user_id, code)
        return code

    async def get_referral_code(self, user_id: int) -> str:
        """Obtém código de referral do usuário"""
        code = await self.db.get_user_referral_code(user_id)
        if not code:
            code = await self.generate_referral_code(user_id)
        return code

    async def use_referral_code(self, new_user_id: int, referral_code: str) -> dict:
        """Usa código de referral ao se cadastrar"""
        try:
            # Verificar se código existe
            referrer_id = await self.db.get_user_by_referral_code(referral_code)

            if not referrer_id:
                return {"success": False, "message": "Código inválido"}

            if referrer_id == new_user_id:
                return {"success": False, "message": "Você não pode usar seu próprio código"}

            # Verificar se usuário já usou algum código
            if await self.db.user_has_referrer(new_user_id):
                return {"success": False, "message": "Você já usou um código de indicação"}

            # Registrar indicação
            await self.db.set_user_referrer(new_user_id, referrer_id)

            # Dar bônus ao novo usuário
            await self.db.add_balance(new_user_id, REFERRAL_BONUS)

            # Dar bônus ao indicador
            await self.db.add_balance(referrer_id, REFERRAL_BONUS * 2)

            # Incrementar contador de indicações
            await self.db.increment_referral_count(referrer_id)

            logger.info(f"Referral usado: {referral_code} | Novo: {new_user_id} | Indicador: {referrer_id}")

            return {
                "success": True,
                "bonus_new_user": REFERRAL_BONUS,
                "bonus_referrer": REFERRAL_BONUS * 2
            }

        except Exception as e:
            logger.error(f"Erro ao usar referral: {e}")
            return {"success": False, "message": "Erro ao processar código"}

    async def get_referral_stats(self, user_id: int) -> dict:
        """Obtém estatísticas de indicações do usuário"""
        stats = await self.db.get_referral_stats(user_id)
        return {
            "code": await self.get_referral_code(user_id),
            "total_referrals": stats.get("count", 0),
            "total_earned": stats.get("earned", 0),
            "referrals": stats.get("referrals", [])
        }

    async def calculate_referral_earning(self, referrer_id: int, purchase_amount: float) -> float:
        """Calcula ganho de comissão por compra do indicado"""
        commission = purchase_amount * (REFERRAL_PERCENTAGE / 100)
        await self.db.add_balance(referrer_id, commission)
        await self.db.log_referral_earning(referrer_id, commission)
        return commission
