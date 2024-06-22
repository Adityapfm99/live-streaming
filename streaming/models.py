# streaming/models.py

import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from video_encoding.fields import VideoField
from django import forms

class Stream(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = VideoField(width_field='video_width', height_field='video_height', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    ffmpeg_pid = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title

class Donation(models.Model):
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(default='default@example.com')
    is_email_sent = models.BooleanField(default=False)
    donation_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


class Comment(models.Model):
    username = models.CharField(max_length=255)
    content = models.TextField()
    stream = models.ForeignKey(Stream, related_name='comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f'{self.user.username}: {self.content[:20]}'

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('virtual_account', 'Virtual Account'),
        ('credit_card', 'Credit Card')

    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)