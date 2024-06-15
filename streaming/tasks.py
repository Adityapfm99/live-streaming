# streaming/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from .models import Donation

@shared_task
def process_donation(donation_id):
    donation = Donation.objects.get(id=donation_id)
    # Implement the logic to process the donation
    donation.is_confirmed = True
    donation.save()
    # Optionally send a notification email
    send_mail(
        'Donation Received',
        'Thank you for your donation!',
        'adityapfm99@gmail.com',
        [donation.user.email],
        fail_silently=False,
    )
