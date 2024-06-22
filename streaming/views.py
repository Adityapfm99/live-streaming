# streaming/views.py

from asyncio import subprocess
from asyncio.log import logger
import base64
from datetime import time
import signal
import ssl
import certifi
from django.contrib.auth import login, authenticate
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import time
import logging

import requests
from .models import Payment
from .form import PaymentForm 
from django.contrib.auth.models import User
from django.shortcuts import render,redirect
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, HttpResponse, JsonResponse
import subprocess
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.views import APIView
from rest_framework import generics,status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer, DonationSerializer, CommentSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import Donation, Comment, Stream
from .serializers import UserSerializer, StreamSerializer, DonationSerializer, CommentSerializer
from .models import Donation
from django.conf import settings
import os
from django.contrib.auth.models import User
from django_rq import get_queue
from .tasks import send_donation_email
import midtransclient
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .snap import Snap 
from .models import Payment
from django.contrib.auth.forms import AuthenticationForm

def index(request):
    return render(request, 'index.html')

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

class StartStreamView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            stream = Stream.objects.get(pk=pk, user=request.user)
            self.start_ffmpeg(stream.id)
            return Response({'status': 'Stream started'}, status=status.HTTP_200_OK)
        except Stream.DoesNotExist:
            return Response({'error': 'Stream not found'}, status=status.HTTP_404_NOT_FOUND)

    def start_ffmpeg(self, stream_id):
        ffmpeg_command = [
            'ffmpeg', '-i', f'rtmp://127.0.0.1/live/{stream_id}',
            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
            '-c:a', 'aac', '-strict', '-2', '-f', 'hls',
            '-hls_time', '3', '-hls_playlist_type', 'event',
            f'/usr/local/var/www/hls/{stream_id}.m3u8'
        ]
        subprocess.Popen(ffmpeg_command)

class StopStreamView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            stream = Stream.objects.get(pk=pk, user=request.user)
            if stream and stream.ffmpeg_pid:
                self.stop_ffmpeg(stream.ffmpeg_pid)
                stream.ffmpeg_pid = None
                stream.save()
                return Response({'status': 'Stream stopped'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Stream not running'}, status=status.HTTP_400_BAD_REQUEST)
        except Stream.DoesNotExist:
            return Response({'error': 'Stream not found'}, status=status.HTTP_404_NOT_FOUND)

    def stop_ffmpeg(self, pid):
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class StreamVideoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        file_path = os.path.join(settings.HLS_ROOT, f'{pk}.m3u8')
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return HttpResponse(f.read(), content_type="application/x-mpegURL")
        else:
            raise Http404

class CreateStreamView(generics.CreateAPIView):
    queryset = Stream.objects.all()
    serializer_class = StreamSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        stream = serializer.save(user=self.request.user)
       
        return Response({'stream_id': stream.id})
                        
class ConfirmDonationView(generics.UpdateAPIView):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        donation = self.get_object()
        if donation.user == request.user:
            donation.is_confirmed = True
            donation.save()
        return Response(DonationSerializer(donation).data)

class CreateCommentView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'request': self.request
        })
        return context

    def perform_create(self, serializer):
        comment = serializer.save()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'stream_{comment.stream.id}',
            {
                'type': 'chat_message',
                'comment': {
                    'username': comment.username,
                    'content': comment.content,
                }
            }
        )
class StreamCommentsView(generics.ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        stream_id = self.kwargs['stream_id']
        return Comment.objects.filter(stream_id=stream_id).order_by('-created_at')


logger = logging.getLogger(__name__)
# @login_required
class CustomSnap(Snap):
    def create_transaction(self, transaction_data):
        headers = {
            'Authorization': 'Basic ' + base64.b64encode((self.server_key + ':').encode()).decode(),
            'Content-Type': 'application/json'
        }
        response = requests.post(f'{self.base_url}/transactions', json=transaction_data, headers=headers, verify=False)
        response.raise_for_status() 
        return response.json()

@csrf_exempt
def donate(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            payment_method = form.cleaned_data['payment_method']
            email = form.cleaned_data['email']  # Get email from form
            
            payment = form.save(commit=False)
            if request.user.is_authenticated:
                payment.user = request.user
                user_email = request.user.email
            else:
                anonymous_user, created = User.objects.get_or_create(username='anonymous')
                payment.user = anonymous_user
                user_email = email
            payment.save()
            
            snap = CustomSnap(
                is_production=settings.MIDTRANS_IS_PRODUCTION,
                server_key=settings.MIDTRANS_SERVER_KEY,
                client_key=settings.MIDTRANS_CLIENT_KEY
            )

            transaction_data = {
                'transaction_details': {
                    'order_id': f'{request.user.id}-{int(time.time())}',
                    'gross_amount': float(amount)
                },
                'credit_card': {
                    'secure': True
                },
                'customer_details': {
                    'first_name': request.user.first_name if request.user.is_authenticated else 'Anonymous',
                    'last_name': request.user.last_name if request.user.is_authenticated else '',
                    'email': user_email,
                    'phone': '0811111111'
                },
                'enabled_payments': []
            }

            if payment_method == 'virtual_account':
                transaction_data['enabled_payments'].extend(['bca_va', 'bni_va', 'bri_va'])
            elif payment_method == 'credit_card':
                transaction_data['enabled_payments'].append('credit_card')
                transaction_data['credit_card']['number'] = form.cleaned_data['cc_number']
                transaction_data['credit_card']['name'] = form.cleaned_data['cc_name']
                transaction_data['credit_card']['cvv'] = form.cleaned_data['cc_cvv']

            try:
                transaction = snap.create_transaction(transaction_data)
                transaction_token = transaction['token']

                queue = get_queue('default')
                print("==============user======================", user_email)
                queue.enqueue(send_donation_email, user_email, float(amount))

                return JsonResponse({'token': transaction_token})
            except requests.exceptions.SSLError as e:
                logger.error(f"SSL error: {str(e)}")
                return JsonResponse({'error': str(e)}, status=401)
            except Exception as e:
                logger.error(f"Error: {str(e)}")
                return JsonResponse({'error': str(e)}, status=401)
        
    else:
        form = PaymentForm()
    return render(request, 'donate.html', {'form': form})

def test_email_view(request):
    send_donation_email('adityapfm99@gmail.com', 13.00)
    return HttpResponse("Test email sent")

@csrf_exempt
def midtrans_notification(request):
    notif_body = json.loads(request.body)
    order_id = notif_body['order_id']
    transaction_status = notif_body['transaction_status']
    fraud_status = notif_body['fraud_status']
    
    try:
        payment = Payment.objects.get(transaction_id=order_id)
        if transaction_status == 'capture':
            if fraud_status == 'challenge':
                payment.status = 'challenge'
            elif fraud_status == 'accept':
                payment.status = 'success'
        elif transaction_status == 'settlement':
            payment.status = 'success'
        elif transaction_status in ['cancel', 'deny', 'expire']:
            payment.status = 'failed'
        elif transaction_status == 'pending':
            payment.status = 'pending'

        payment.save()
    except Payment.DoesNotExist:
        pass

    return JsonResponse({'status': 'ok'})

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('donate')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})