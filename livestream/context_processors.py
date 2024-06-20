from django.conf import settings

def midtrans_client_key(request):
    return {
        'client_key': settings.MIDTRANS_CLIENT_KEY
    }
