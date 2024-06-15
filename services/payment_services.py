import midtransclient
from django.conf import settings

def create_midtrans_transaction(order_id, gross_amount):
    snap = midtransclient.Snap(
        is_production=False,  
        server_key=settings.MIDTRANS_SERVER_KEY,
        client_key=settings.MIDTRANS_CLIENT_KEY
    )
    param = {
        "transaction_details": {
            "order_id": order_id,
            "gross_amount": gross_amount,
        },
        "credit_card": {
            "secure": True
        }
    }
    transaction = snap.create_transaction(param)
    return transaction['redirect_url']
