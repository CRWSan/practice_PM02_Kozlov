"""
External API integrations
"""
import json
import requests
from typing import Optional, Dict
from ..application.interfaces import IPaymentService


class PaymentService(IPaymentService):
    """Payment service implementation"""
    
    def __init__(self, api_key: str = "", base_url: str = "https://api.payment.com"):
        self.api_key = api_key
        self.base_url = base_url
        self._success_rate = 0.95  # 95% success rate for testing
    
    def process_payment(self, booking_id: str, amount: float) -> bool:
        """Process payment for a booking"""
        # Simulate payment processing
        # In real implementation, this would call an external API
        
        if amount <= 0:
            return False
        
        # Simulate random failure (for testing)
        import random
        if random.random() > self._success_rate:
            return False
        
        # Simulate API call
        return True
    
    def refund_payment(self, booking_id: str) -> bool:
        """Refund payment for a booking"""
        # Simulate refund processing
        return True
    
    def set_success_rate(self, rate: float) -> None:
        """Set success rate for testing"""
        self._success_rate = rate


class ExternalHotelAPI:
    """External hotel API client"""
    
    def __init__(self, base_url: str = "https://api.hotels.com"):
        self.base_url = base_url
    
    def get_hotel_details(self, hotel_id: int) -> Optional[Dict]:
        """Get hotel details from external API"""
        # Simulated API call
        try:
            response = requests.get(f"{self.base_url}/hotels/{hotel_id}")
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return None
    
    def search_hotels(self, city: str, check_in: str, check_out: str) -> List[Dict]:
        """Search hotels via external API"""
        # Simulated API call
        try:
            params = {
                "city": city,
                "check_in": check_in,
                "check_out": check_out
            }
            response = requests.get(f"{self.base_url}/search", params=params)
            if response.status_code == 200:
                return response.json().get("hotels", [])
        except requests.RequestException:
            pass
        return []