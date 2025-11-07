"""
Módulo de integração com Apex Seguidores API v2
Serviços de redes sociais: seguidores, curtidas, visualizações, etc.
"""

import requests
import logging
from typing import Optional, List, Dict
from config import Config

logger = logging.getLogger(__name__)


class ApexSeguidoresAPI:
    """Cliente para API Apex Seguidores"""

    def __init__(self):
        self.base_url = 'https://apexseguidores.com/api/v2'
        self.api_key = Config.APEX_API_KEY

    def _make_request(self, params: Dict) -> Optional[Dict]:
        """Faz requisição à API"""
        try:
            params['key'] = self.api_key

            response = requests.post(
                self.base_url,
                data=params,
                timeout=30
            )
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Apex API error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    def get_services(self) -> Optional[List[Dict]]:
        """
        Lista todos os serviços disponíveis

        Returns:
            Lista de serviços com id, nome, preço, min, max, etc.
        """
        result = self._make_request({'action': 'services'})

        if result:
            logger.info(f"Retrieved {len(result)} services from Apex")
            return result

        return None

    def get_balance(self) -> Optional[float]:
        """
        Consulta saldo da conta Apex

        Returns:
            Saldo em reais ou None
        """
        result = self._make_request({'action': 'balance'})

        if result and 'balance' in result:
            balance = float(result['balance'])
            logger.info(f"Apex balance: R$ {balance:.2f}")
            return balance

        return None

    def create_order(
        self, 
        service_id: int,
        link: str,
        quantity: int
    ) -> Optional[Dict]:
        """
        Cria um pedido de serviço

        Args:
            service_id: ID do serviço (obtido via get_services)
            link: Link do perfil/post (Instagram, TikTok, etc)
            quantity: Quantidade desejada

        Returns:
            Dict com order_id e informações do pedido
        """
        params = {
            'action': 'add',
            'service': service_id,
            'link': link,
            'quantity': quantity
        }

        result = self._make_request(params)

        if result and 'order' in result:
            order_id = result['order']
            logger.info(f"Order created: {order_id} - Service: {service_id}, Qty: {quantity}")
            return {
                'order_id': order_id,
                'service_id': service_id,
                'link': link,
                'quantity': quantity,
                'status': 'Pending'
            }

        return None

    def check_order_status(self, order_id: int) -> Optional[Dict]:
        """
        Verifica status de um pedido

        Args:
            order_id: ID do pedido

        Returns:
            Dict com status, charge, start_count, remains, etc.
        """
        params = {
            'action': 'status',
            'order': order_id
        }

        result = self._make_request(params)

        if result:
            return {
                'order_id': order_id,
                'status': result.get('status'),
                'charge': result.get('charge'),
                'start_count': result.get('start_count'),
                'remains': result.get('remains'),
                'currency': result.get('currency', 'BRL')
            }

        return None

    # Alias para compatibilidade
    def get_order_status(self, order_id: int) -> Optional[Dict]:
        """Alias para check_order_status"""
        return self.check_order_status(order_id)

    def get_services_by_category(self, category: str = None) -> List[Dict]:
        """
        Filtra serviços por categoria

        Args:
            category: instagram, tiktok, youtube, twitter, etc.

        Returns:
            Lista de serviços filtrados
        """
        all_services = self.get_services()

        if not all_services:
            return []

        if not category:
            return all_services

        # Filtrar por nome/categoria
        category_lower = category.lower()
        filtered = [
            s for s in all_services 
            if category_lower in s.get('name', '').lower() 
            or category_lower in s.get('category', '').lower()
        ]

        logger.info(f"Found {len(filtered)} services for category: {category}")
        return filtered

    def format_service_info(self, service: Dict) -> str:
        """Formata informações de um serviço"""
        name = service.get('name', 'N/A')
        price = float(service.get('rate', 0))
        min_qty = service.get('min', 0)
        max_qty = service.get('max', 0)

        return (
            f"📦 {name}\n"
            f"💰 Preço: R$ {price:.2f} por 1000\n"
            f"📊 Min: {min_qty} | Max: {max_qty}"
        )

    def get_multiple_orders_status(self, order_ids: List[int]) -> Dict[int, Optional[Dict]]:
        """
        Verifica status de múltiplos pedidos

        Args:
            order_ids: Lista de IDs dos pedidos

        Returns:
            Dict com order_id como chave e status como valor
        """
        results = {}
        for order_id in order_ids:
            results[order_id] = self.check_order_status(order_id)
        return results


# Instância global
apex_api = ApexSeguidoresAPI()
