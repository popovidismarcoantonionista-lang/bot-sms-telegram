import requests
import logging
from typing import Optional, Dict
from config import Config

logger = logging.getLogger(__name__)

class SMSActivate:
    """SMS-Activate API client"""

    def __init__(self):
        self.api_key = Config.SMS_ACTIVATE_API_KEY
        self.base_url = Config.SMS_ACTIVATE_BASE_URL

    def _make_request(self, params: Dict) -> str:
        """Make request to SMS-Activate API"""
        try:
            params['api_key'] = self.api_key
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"SMS-Activate API error: {e}")
            raise

    def get_balance(self) -> Optional[float]:
        """Get account balance"""
        try:
            result = self._make_request({'action': 'getBalance'})
            if result.startswith('ACCESS_BALANCE:'):
                balance = float(result.split(':')[1])
                logger.info(f"SMS-Activate balance: ${balance}")
                return balance
            return None
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return None

    def get_number(self, service: str, country: str = '0') -> Optional[Dict]:
        """Get a phone number for service"""
        try:
            result = self._make_request({
                'action': 'getNumber',
                'service': service,
                'country': country
            })

            if result.startswith('ACCESS_NUMBER'):
                parts = result.split(':')
                activation_id = parts[1]
                phone_number = parts[2]

                logger.info(f"Got number: {phone_number} (ID: {activation_id})")
                return {
                    'activation_id': activation_id,
                    'phone_number': phone_number
                }
            elif result == 'NO_NUMBERS':
                logger.warning(f"No numbers available for service: {service}")
                return None
            else:
                logger.error(f"Unexpected response: {result}")
                return None

        except Exception as e:
            logger.error(f"Error getting number: {e}")
            return None

    def get_status(self, activation_id: str) -> Optional[str]:
        """Get activation status and SMS code"""
        try:
            result = self._make_request({
                'action': 'getStatus',
                'id': activation_id
            })

            if result.startswith('STATUS_OK'):
                # SMS received
                sms_code = result.split(':')[1]
                logger.info(f"SMS received for {activation_id}: {sms_code}")
                return sms_code
            elif result == 'STATUS_WAIT_CODE':
                # Waiting for SMS
                return 'WAITING'
            elif result == 'STATUS_WAIT_RETRY':
                # Can retry
                return 'RETRY'
            else:
                logger.warning(f"Status for {activation_id}: {result}")
                return result

        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return None

    def set_status(self, activation_id: str, status: int) -> bool:
        """Set activation status (1=ready, 6=complete, 8=cancel)"""
        try:
            result = self._make_request({
                'action': 'setStatus',
                'id': activation_id,
                'status': str(status)
            })

            if result.startswith('ACCESS_'):
                logger.info(f"Set status {status} for {activation_id}")
                return True
            else:
                logger.error(f"Failed to set status: {result}")
                return False

        except Exception as e:
            logger.error(f"Error setting status: {e}")
            return False

    def cancel_activation(self, activation_id: str) -> bool:
        """Cancel activation and get refund"""
        return self.set_status(activation_id, 8)

    def complete_activation(self, activation_id: str) -> bool:
        """Mark activation as complete"""
        return self.set_status(activation_id, 6)

# Global instance
sms_activate = SMSActivate()
