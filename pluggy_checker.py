import requests
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from config import Config

logger = logging.getLogger(__name__)

class PluggyChecker:
    """Check Pluggy transactions for deposits"""

    def __init__(self):
        self.base_url = Config.PLUGGY_BASE_URL
        self.client_id = Config.PLUGGY_CLIENT_ID
        self.client_secret = Config.PLUGGY_CLIENT_SECRET
        self.item_id = Config.PLUGGY_ITEM_ID
        self.access_token = None
        self.token_expires_at = None

    def _get_access_token(self) -> str:
        """Get or refresh Pluggy access token"""
        # Check if token is still valid
        if self.access_token and self.token_expires_at:
            if datetime.utcnow() < self.token_expires_at:
                return self.access_token

        # Get new token
        try:
            response = requests.post(
                f"{self.base_url}/auth",
                json={
                    "clientId": self.client_id,
                    "clientSecret": self.client_secret
                },
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()

            self.access_token = data['apiKey']
            # Token expires in 24 hours, refresh 1 hour before
            self.token_expires_at = datetime.utcnow() + timedelta(hours=23)

            logger.info("Successfully obtained Pluggy access token")
            return self.access_token

        except Exception as e:
            logger.error(f"Error getting Pluggy access token: {e}")
            raise

    def get_recent_transactions(self, days: int = 1) -> List[Dict]:
        """Get recent transactions from Pluggy"""
        try:
            token = self._get_access_token()

            # Calculate date range
            to_date = datetime.utcnow()
            from_date = to_date - timedelta(days=days)

            # Get transactions
            response = requests.get(
                f"{self.base_url}/transactions",
                params={
                    "itemId": self.item_id,
                    "from": from_date.strftime("%Y-%m-%d"),
                    "to": to_date.strftime("%Y-%m-%d"),
                    "pageSize": 100
                },
                headers={
                    "X-API-KEY": token,
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            data = response.json()

            transactions = data.get('results', [])
            logger.info(f"Retrieved {len(transactions)} transactions from Pluggy")

            return transactions

        except Exception as e:
            logger.error(f"Error getting Pluggy transactions: {e}")
            return []

    def find_deposit_by_description(self, description: str, min_amount: float = 0.0) -> Optional[Dict]:
        """Find a transaction by description (user deposit ID)"""
        try:
            transactions = self.get_recent_transactions(days=7)  # Last 7 days

            for trans in transactions:
                # Check if it's a credit (incoming) transaction
                if trans.get('type') != 'DEBIT':  # We want CREDIT transactions
                    trans_desc = trans.get('description', '').upper()
                    trans_amount = abs(float(trans.get('amount', 0)))

                    # Check if description contains deposit ID and amount is positive
                    if description.upper() in trans_desc and trans_amount >= min_amount:
                        logger.info(f"Found matching deposit: {trans['id']} - R$ {trans_amount}")
                        return trans

            return None

        except Exception as e:
            logger.error(f"Error finding deposit: {e}")
            return None

    def get_account_balance(self) -> Optional[float]:
        """Get current account balance"""
        try:
            token = self._get_access_token()

            response = requests.get(
                f"{self.base_url}/accounts",
                params={"itemId": self.item_id},
                headers={
                    "X-API-KEY": token,
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            data = response.json()

            accounts = data.get('results', [])
            if accounts:
                balance = float(accounts[0].get('balance', 0))
                logger.info(f"Account balance: R$ {balance}")
                return balance

            return None

        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            return None

# Global instance
pluggy_checker = PluggyChecker()
