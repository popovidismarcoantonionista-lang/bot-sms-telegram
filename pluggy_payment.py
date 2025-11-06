"""
Módulo para integração de pagamentos Pix via Pluggy.ai
Suporta geração de código Pix cópia e cola e verificação de pagamentos
"""

import requests
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
from config import Config

logger = logging.getLogger(__name__)


class PluggyPaymentAPI:
    """Cliente para API de Pagamentos Pluggy.ai"""

    def __init__(self):
        self.base_url = 'https://api.pluggy.ai'
        self.client_id = Config.PLUGGY_CLIENT_ID
        self.client_secret = Config.PLUGGY_CLIENT_SECRET
        self.recipient_id = Config.PLUGGY_RECIPIENT_ID
        self.api_key = Config.PLUGGY_API_KEY
        self.environment = Config.PLUGGY_ENVIRONMENT

        # Headers para requisições
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': self.api_key
        }

    def criar_pagamento_pix(
        self, 
        valor: float, 
        descricao: str, 
        user_id: int,
        callback_urls: Optional[Dict[str, str]] = None
    ) -> Optional[Dict]:
        """
        Cria uma requisição de pagamento Pix e retorna o código cópia e cola

        Args:
            valor: Valor em reais (ex: 5.00)
            descricao: Descrição do pagamento
            user_id: ID do usuário no Telegram
            callback_urls: URLs de callback (opcional)

        Returns:
            Dict com dados do pagamento incluindo pixQrCode, ou None em caso de erro
        """
        try:
            endpoint = f'{self.base_url}/payments/requests'

            # ID único do pagamento para rastreamento
            client_payment_id = f'sms_{user_id}_{int(datetime.now().timestamp())}'

            payload = {
                'amount': float(valor),
                'description': descricao,
                'recipientId': self.recipient_id,
                'clientPaymentId': client_payment_id,
                'isSandbox': self.environment == 'sandbox'
            }

            # Adicionar URLs de callback se fornecidas
            if callback_urls:
                payload['callbackUrls'] = callback_urls

            logger.info(f"Creating Pix payment: R$ {valor} for user {user_id}")

            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Payment created successfully: {data.get('id')}")

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating Pix payment: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"API Response: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating payment: {e}")
            return None

    def consultar_pagamento(self, payment_id: str) -> Optional[Dict]:
        """
        Consulta o status de um pagamento pelo ID

        Args:
            payment_id: ID do pagamento retornado na criação

        Returns:
            Dict com dados atualizados do pagamento, ou None em caso de erro
        """
        try:
            endpoint = f'{self.base_url}/payments/requests/{payment_id}'

            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Payment status: {data.get('status')} - {payment_id}")

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking payment status: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error checking payment: {e}")
            return None

    def verificar_pagamento_concluido(self, payment_id: str) -> bool:
        """
        Verifica se um pagamento foi concluído

        Args:
            payment_id: ID do pagamento

        Returns:
            True se pagamento foi concluído, False caso contrário
        """
        pagamento = self.consultar_pagamento(payment_id)

        if not pagamento:
            return False

        status = pagamento.get('status', '')
        return status == 'COMPLETED'

    def get_status_emoji(self, status: str) -> str:
        """Retorna emoji apropriado para cada status"""
        status_map = {
            'CREATED': '⏳',
            'SCHEDULED': '📅',
            'AUTHORIZED': '✅',
            'IN_PROGRESS': '🔄',
            'COMPLETED': '✅',
            'WAITING_PAYER_AUTHORIZATION': '⏰',
            'CANCELED': '❌',
            'EXPIRED': '⏱',
            'ERROR': '❌'
        }
        return status_map.get(status, '❓')

    def get_status_description(self, status: str) -> str:
        """Retorna descrição em português para cada status"""
        descriptions = {
            'CREATED': 'Aguardando Pagamento',
            'SCHEDULED': 'Agendado',
            'AUTHORIZED': 'Autorizado',
            'IN_PROGRESS': 'Processando',
            'COMPLETED': 'Pago ✓',
            'WAITING_PAYER_AUTHORIZATION': 'Aguardando Autorização',
            'CANCELED': 'Cancelado',
            'EXPIRED': 'Expirado',
            'ERROR': 'Erro no Pagamento'
        }
        return descriptions.get(status, 'Status Desconhecido')


# Instância global
pluggy_payment = PluggyPaymentAPI()
