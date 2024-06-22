import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

def send_donation_email(to_email, amount):
    logger.info(f'Sending donation email to {to_email} for amount ${amount:.2f}')
    
    subject = 'Donation Received'
    message = f'Thank you for your donation of ${amount:.2f}.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [to_email]

    try:
        send_mail(subject, message, from_email, recipient_list)
        logger.info('Email sent successfully')
    except Exception as e:
        logger.error(f'Failed to send email: {e}')