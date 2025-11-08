"""
Sistema de Fidelidade e Níveis
Bronze → Silver → Gold → Platinum
"""

import logging
from database import Database
from enum import Enum

logger = logging.getLogger(__name__)

class UserLevel(Enum):
    BRONZE = ("Bronze", 0, 0, "🥉")
    SILVER = ("Silver", 100, 2, "🥈")
    GOLD = ("Gold", 500, 5, "🥇")
    PLATINUM = ("Platinum", 1000, 10, "💎")

    def __init__(self, name, min_spent, cashback_percent, emoji):
        self.level_name = name
        self.min_spent = min_spent
        self.cashback_percent = cashback_percent
        self.emoji = emoji

class LoyaltySystem:
    def __init__(self, db: Database):
        self.db = db

    async def get_user_level(self, user_id: int) -> UserLevel:
        """Obtém nível atual do usuário baseado no total gasto"""
        total_spent = await self.db.get_total_spent(user_id)

        for level in reversed(list(UserLevel)):
            if total_spent >= level.min_spent:
                return level

        return UserLevel.BRONZE

    async def calculate_cashback(self, user_id: int, purchase_amount: float) -> float:
        """Calcula cashback baseado no nível do usuário"""
        level = await self.get_user_level(user_id)
        cashback = purchase_amount * (level.cashback_percent / 100)

        if cashback > 0:
            await self.db.add_balance(user_id, cashback)
            await self.db.log_cashback(user_id, cashback, level.level_name)
            logger.info(f"Cashback: User {user_id} | Nível {level.level_name} | R$ {cashback:.2f}")

        return cashback

    async def get_progress_to_next_level(self, user_id: int) -> dict:
        """Retorna progresso para o próximo nível"""
        current_level = await self.get_user_level(user_id)
        total_spent = await self.db.get_total_spent(user_id)

        levels_list = list(UserLevel)
        current_index = levels_list.index(current_level)

        if current_index == len(levels_list) - 1:
            # Já está no nível máximo
            return {
                "current_level": current_level.level_name,
                "current_emoji": current_level.emoji,
                "is_max_level": True,
                "total_spent": total_spent
            }

        next_level = levels_list[current_index + 1]
        remaining = next_level.min_spent - total_spent
        progress_percent = (total_spent / next_level.min_spent) * 100

        return {
            "current_level": current_level.level_name,
            "current_emoji": current_level.emoji,
            "next_level": next_level.level_name,
            "next_emoji": next_level.emoji,
            "total_spent": total_spent,
            "remaining": remaining,
            "progress_percent": progress_percent,
            "is_max_level": False
        }

    async def get_level_benefits(self, level: UserLevel) -> str:
        """Retorna texto com benefícios do nível"""
        benefits = f"{level.emoji} **Nível {level.level_name}**\\n\\n"
        benefits += f"💰 Cashback: {level.cashback_percent}%\\n"
        benefits += f"📊 Gasto mínimo: R$ {level.min_spent}\\n"

        if level == UserLevel.BRONZE:
            benefits += "✨ Acesso básico aos serviços"
        elif level == UserLevel.SILVER:
            benefits += "✨ Prioridade no atendimento\\n"
            benefits += "🎁 Bônus em promoções"
        elif level == UserLevel.GOLD:
            benefits += "✨ Atendimento VIP\\n"
            benefits += "🎁 Bônus extras em promoções\\n"
            benefits += "📱 Acesso antecipado a novos serviços"
        elif level == UserLevel.PLATINUM:
            benefits += "✨ Atendimento Premium 24/7\\n"
            benefits += "🎁 Maiores bônus e ofertas exclusivas\\n"
            benefits += "📱 Acesso antecipado e beta tester\\n"
            benefits += "💎 Descontos especiais permanentes"

        return benefits
