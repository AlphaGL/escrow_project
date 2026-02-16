"""
Paystack API integration service
Handles payment initialization and verification
"""
import requests
from django.conf import settings
from decimal import Decimal


class PaystackService:
    """Service class for Paystack API integration"""
    
    BASE_URL = "https://api.paystack.co"
    
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.public_key = settings.PAYSTACK_PUBLIC_KEY
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json',
        }
    
    def initialize_payment(self, email, amount, reference, callback_url=None):
        """
        Initialize a payment transaction
        
        Args:
            email: Customer's email
            amount: Amount in kobo (multiply naira by 100)
            reference: Unique transaction reference
            callback_url: URL to redirect after payment
        
        Returns:
            dict: Response from Paystack API
        """
        url = f"{self.BASE_URL}/transaction/initialize"
        
        # Convert amount to kobo (smallest currency unit)
        amount_in_kobo = int(Decimal(amount) * 100)
        
        data = {
            'email': email,
            'amount': amount_in_kobo,
            'reference': reference,
            'callback_url': callback_url or settings.PAYSTACK_CALLBACK_URL,
            'metadata': {
                'custom_fields': [
                    {
                        'display_name': 'Platform',
                        'variable_name': 'platform',
                        'value': 'SafeRelease Nigeria'
                    }
                ]
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'status': False,
                'message': f'Payment initialization failed: {str(e)}'
            }
    
    def verify_payment(self, reference):
        """
        Verify a payment transaction
        
        Args:
            reference: Transaction reference to verify
        
        Returns:
            dict: Verification response from Paystack
        """
        url = f"{self.BASE_URL}/transaction/verify/{reference}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'status': False,
                'message': f'Payment verification failed: {str(e)}'
            }
    
    def initiate_transfer(self, amount, recipient_code, reason='Withdrawal'):
        """
        Initiate a transfer (payout) to a recipient
        
        Args:
            amount: Amount in kobo
            recipient_code: Paystack recipient code
            reason: Reason for transfer
        
        Returns:
            dict: Response from Paystack API
        """
        url = f"{self.BASE_URL}/transfer"
        
        amount_in_kobo = int(Decimal(amount) * 100)
        
        data = {
            'source': 'balance',
            'amount': amount_in_kobo,
            'recipient': recipient_code,
            'reason': reason,
        }
        
        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'status': False,
                'message': f'Transfer initiation failed: {str(e)}'
            }
    
    def create_transfer_recipient(self, name, account_number, bank_code):
        """
        Create a transfer recipient
        
        Args:
            name: Account name
            account_number: Bank account number
            bank_code: Paystack bank code
        
        Returns:
            dict: Response with recipient code
        """
        url = f"{self.BASE_URL}/transferrecipient"
        
        data = {
            'type': 'nuban',
            'name': name,
            'account_number': account_number,
            'bank_code': bank_code,
            'currency': 'NGN',
        }
        
        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'status': False,
                'message': f'Recipient creation failed: {str(e)}'
            }
    
    def verify_account_number(self, account_number, bank_code):
        """
        Verify bank account number
        
        Args:
            account_number: Account number to verify
            bank_code: Bank code
        
        Returns:
            dict: Account details if valid
        """
        url = f"{self.BASE_URL}/bank/resolve"
        
        params = {
            'account_number': account_number,
            'bank_code': bank_code,
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'status': False,
                'message': f'Account verification failed: {str(e)}'
            }
    
    def get_banks(self):
        """
        Get list of supported banks
        
        Returns:
            dict: List of banks with codes
        """
        url = f"{self.BASE_URL}/bank"
        
        params = {
            'country': 'nigeria',
            'use_cursor': False,
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'status': False,
                'message': f'Failed to fetch banks: {str(e)}'
            }


# Singleton instance
paystack = PaystackService()
