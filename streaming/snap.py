# payments/snap.py
import requests
import base64
import certifi
import ssl

class Snap:
    def __init__(self, is_production, server_key, client_key):
        self.is_production = is_production
        self.server_key = server_key
        self.client_key = client_key
        self.base_url = 'https://app.midtrans.com/snap/v1' if is_production else 'https://app.sandbox.midtrans.com/snap/v1'
        self.context = ssl.create_default_context(cafile=certifi.where())

    def create_transaction(self, transaction_data):
        headers = {
            'Authorization': 'Basic ' + base64.b64encode((self.server_key + ':').encode()).decode(),
            'Content-Type': 'application/json'
        }
        response = requests.post(f'{self.base_url}/transactions', json=transaction_data, headers=headers, verify=self.context)
        response.raise_for_status()  # This will raise an error for HTTP error codes
        return response.json()
