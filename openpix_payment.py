"""
Módulo de pagamentos PIX usando OpenPix API
Gera códigos Pix cópia e cola de forma simples e eficiente
Gratuito até 1000 transações/mês
"""

import requests
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
from config import Config

logger = logging.getLogger(__name__)


class OpenPixAPI:
    """Cliente para API OpenPix (Woovi)"""

    def __init__(self):
        self.base_url = 'https://api.openpix.com.br/api/v1'
        self.app_id = Config.OPENPIX_APP_ID
        self.headers = {
            'Authorization': self.app_id,
            'Content-Type': 'application/json'
        }

    def criar_cobranca_pix(
        self, 
        valor: int,  # Valor em centavos (ex: 1000 = R$ 10,00)
        descricao: str,
        user_id: int,
        expira_em_segundos: int = 3600
    ) -> Optional[Dict]:
        """
        Cria uma cobrança PIX e retorna o código cópia e cola

        Args:
            valor: Valor em centavos (1000 = R$ 10,00)
            descricao: Descrição da cobrança
            user_id: ID do usuário
            expira_em_segundos: Tempo até expirar (padrão: 1 hora)

        Returns:
            Dict com 'brCode' (código cópia e cola), 'qrCodeImage', 'correlationID', etc.
        """
        try:
            # Criar ID único para rastreamento
            correlation_id = f"sms_{user_id}_{int(datetime.now().timestamp())}"

            payload = {
                "correlationID": correlation_id,
                "value": valor,
                "comment": descricao,
                "expiresIn": expira_em_segundos,
                "customer": {
                    "name": f"User {user_id}",
                    "taxID": str(user_id)
                }
            }

            logger.info(f"Creating PIX charge: R$ {valor/100:.2f} for user {user_id}")

            response = requests.post(
                f'{self.base_url}/charge',
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()

            data = response.json()
            charge = data.get('charge', {})

            logger.info(f"PIX charge created: {charge.get('correlationID')}")

            return {
                'correlation_id': charge.get('correlationID'),
                'brcode': charge.get('brCode'),  # Código cópia e cola
                'qrcode_image': charge.get('qrCodeImage'),  # URL da imagem QR
                'expires_at': charge.get('expiresDate'),
                'status': charge.get('status'),
                'value': charge.get('value'),
                'transaction_id': charge.get('transactionID')
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating PIX charge: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"API Response: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    def consultar_cobranca(self, correlation_id: str) -> Optional[Dict]:
        """
        Consulta status de uma cobrança pelo correlation_id

        Args:
            correlation_id: ID único da cobrança

        Returns:
            Dict com dados da cobrança
        """
        try:
            response = requests.get(
                f'{self.base_url}/charge',
                params={'correlationID': correlation_id},
                headers=self.headers
            )
            response.raise_for_status()

            data = response.json()
            charge = data.get('charge', {})

            return {
                'correlation_id': charge.get('correlationID'),
                'status': charge.get('status'),
                'value': charge.get('value'),
                'paid_at': charge.get('paidAt'),
                'brcode': charge.get('brCode')
            }

        except Exception as e:
            logger.error(f"Error checking charge: {e}")
            return None

    def verificar_pagamento_concluido(self, correlation_id: str) -> bool:
        """Verifica se cobrança foi paga"""
        cobranca = self.consultar_cobranca(correlation_id)

        if not cobranca:
            return False

        status = cobranca.get('status', '')
        return status in ['COMPLETED', 'CONFIRMED']

    def get_status_emoji(self, status: str) -> str:
        """Retorna emoji para cada status"""
        status_map = {
            'ACTIVE': '⏳',
            'COMPLETED': '✅',
            'CONFIRMED': '✅',
            'EXPIRED': '⏱',
            'CANCELED': '❌'
        }
        return status_map.get(status, '❓')

    def get_status_description(self, status: str) -> str:
        """Descrição em português"""
        descriptions = {
            'ACTIVE': 'Aguardando Pagamento',
            'COMPLETED': 'Pago ✓',
            'CONFIRMED': 'Pago ✓',
            'EXPIRED': 'Expirado',
            'CANCELED': 'Cancelado'
        }
        return descriptions.get(status, 'Desconhecido')


# Instância global
openpix_api = OpenPixAPI()
