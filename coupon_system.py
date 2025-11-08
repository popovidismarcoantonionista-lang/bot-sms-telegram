"""
Sistema de Cupons de Desconto
"""

import logging
from database import Database
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CouponSystem:
    def __init__(self, db: Database):
        self.db = db

    async def create_coupon(self, code: str, discount_percent: float, 
                           max_uses: int = None, expires_at: datetime = None,
                           min_purchase: float = 0) -> bool:
        """Cria um novo cupom"""
        try:
            await self.db.create_coupon(
                code=code.upper(),
                discount_percent=discount_percent,
                max_uses=max_uses,
                expires_at=expires_at,
                min_purchase=min_purchase
            )
            logger.info(f"Cupom criado: {code} | {discount_percent}% de desconto")
            return True
        except Exception as e:
            logger.error(f"Erro ao criar cupom: {e}")
            return False

    async def validate_coupon(self, code: str, purchase_amount: float, user_id: int) -> dict:
        """Valida um cupom"""
        try:
            coupon = await self.db.get_coupon(code.upper())

            if not coupon:
                return {"valid": False, "message": "Cupom inválido"}

            # Verificar se está ativo
            if not coupon.get("active"):
                return {"valid": False, "message": "Cupom desativado"}

            # Verificar expiração
            if coupon.get("expires_at"):
                if datetime.now() > coupon["expires_at"]:
                    return {"valid": False, "message": "Cupom expirado"}

            # Verificar número de usos
            if coupon.get("max_uses"):
                if coupon.get("current_uses", 0) >= coupon["max_uses"]:
                    return {"valid": False, "message": "Cupom esgotado"}

            # Verificar valor mínimo
            if purchase_amount < coupon.get("min_purchase", 0):
                return {
                    "valid": False, 
                    "message": f"Valor mínimo de compra: R$ {coupon['min_purchase']:.2f}"
                }

            # Verificar se usuário já usou (limite 1 por usuário)
            if await self.db.user_used_coupon(user_id, code.upper()):
                return {"valid": False, "message": "Você já usou este cupom"}

            # Calcular desconto
            discount = purchase_amount * (coupon["discount_percent"] / 100)
            final_amount = purchase_amount - discount

            return {
                "valid": True,
                "discount_percent": coupon["discount_percent"],
                "discount_amount": discount,
                "final_amount": final_amount,
                "code": code.upper()
            }

        except Exception as e:
            logger.error(f"Erro ao validar cupom: {e}")
            return {"valid": False, "message": "Erro ao validar cupom"}

    async def use_coupon(self, code: str, user_id: int) -> bool:
        """Registra uso de um cupom"""
        try:
            await self.db.increment_coupon_uses(code.upper())
            await self.db.register_coupon_usage(user_id, code.upper())
            logger.info(f"Cupom usado: {code} | User {user_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao usar cupom: {e}")
            return False

    async def get_active_coupons(self) -> list:
        """Lista cupons ativos"""
        return await self.db.get_active_coupons()

    async def deactivate_coupon(self, code: str) -> bool:
        """Desativa um cupom"""
        try:
            await self.db.deactivate_coupon(code.upper())
            return True
        except Exception as e:
            logger.error(f"Erro ao desativar cupom: {e}")
            return False
