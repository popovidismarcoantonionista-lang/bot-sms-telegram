"""
Módulo de pagamentos PIX usando Chave PIX Estática
100% Gratuito - Usa Pluggy apenas para verificar depósitos
Perfeito para bots sem CNPJ
"""

import logging
from typing import Optional, Dict
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)


class SimplePIXPayment:
    """
    Gerador de instruções de pagamento PIX usando chave estática
    Verificação de pagamentos via Pluggy (já configurado)
    """

    def __init__(self):
        self.pix_key = Config.PIX_KEY
        self.pix_name = Config.PIX_NAME
        self.pix_city = Config.PIX_CITY

    def gerar_instrucoes_pix(
        self, 
        valor: float, 
        user_id: int,
        descricao: str = "Depósito Bot SMS"
    ) -> Dict:
        """
        Gera instruções de pagamento PIX com ID único para rastreamento

        Args:
            valor: Valor em reais
            user_id: ID do usuário Telegram
            descricao: Descrição do pagamento

        Returns:
            Dict com instruções de pagamento e ID único
        """
        # ID único para rastreamento (será usado no Pluggy)
        payment_id = f"SMS{user_id}{int(datetime.now().timestamp())}"

        instrucoes = {
            'payment_id': payment_id,
            'valor': valor,
            'pix_key': self.pix_key,
            'pix_key_type': 'CPF',
            'recipient_name': self.pix_name,
            'recipient_cpf': self.pix_key,
            'city': self.pix_city,
            'description': descricao,
            'user_id': user_id,
            'created_at': datetime.now().isoformat()
        }

        logger.info(f"PIX instructions created: {payment_id} - R$ {valor} for user {user_id}")

        return instrucoes

    def formatar_mensagem_pix(self, instrucoes: Dict) -> str:
        """
        Formata mensagem bonita para enviar ao usuário

        Args:
            instrucoes: Dict retornado por gerar_instrucoes_pix

        Returns:
            String formatada para Telegram (Markdown)
        """
        valor = instrucoes['valor']
        payment_id = instrucoes['payment_id']
        pix_key = instrucoes['pix_key']
        recipient = instrucoes['recipient_name']

        mensagem = f"""
🎯 *Depósito via PIX*

💰 *Valor:* R$ {valor:.2f}
🆔 *ID do Depósito:* `{payment_id}`

📋 *Dados para Pagamento PIX:*

🔑 *Chave PIX (CPF):*
```
{pix_key}
```

👤 *Favorecido:* {recipient}
📄 *CPF:* {pix_key}

📱 *Como Pagar:*

1️⃣ Abra seu app bancário
2️⃣ Vá em *PIX* → *Transferir*
3️⃣ Escolha *Chave PIX*
4️⃣ Cole a chave: `{pix_key}`
5️⃣ Valor: *R$ {valor:.2f}*
6️⃣ **IMPORTANTE:** Na descrição/mensagem, coloque:
   `{payment_id}`

⚠️ *ATENÇÃO:*
• Use EXATAMENTE o ID `{payment_id}` na descrição
• Sem esse ID, não conseguimos identificar seu pagamento
• O valor deve ser EXATO: R$ {valor:.2f}

⏰ *Após pagar:*
Seu saldo será creditado automaticamente em até 2 minutos!

✅ Verificação automática ativada!
"""

        return mensagem

    def get_status_emoji(self, status: str) -> str:
        """Emoji para cada status"""
        return {
            'pending': '⏳',
            'completed': '✅',
            'failed': '❌',
            'expired': '⏱'
        }.get(status, '❓')


# Instância global
simple_pix = SimplePIXPayment()
