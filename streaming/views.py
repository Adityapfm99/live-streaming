# streaming/views.py

from asyncio import subprocess
from django.contrib.auth.models import User
from django.shortcuts import render,redirect
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, HttpResponse, JsonResponse
import subprocess
from rest_framework.views import APIView
from rest_framework import generics,status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer, DonationSerializer, CommentSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import Donation, Comment, Stream
from .serializers import UserSerializer, StreamSerializer, DonationSerializer, CommentSerializer
from .tasks import process_donation
from .models import Donation
from django.conf import settings
import os
from services.payment_services import create_midtrans_transaction

def index(request):
    return render(request, 'index.html')

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

def create_donation(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        user = request.user
        stream_id = request.POST.get('stream_id')
        donation = Donation.objects.create(user=user, stream_id=stream_id, amount=amount)
        redirect_url = create_midtrans_transaction(donation.id, donation.amount)
        return redirect(redirect_url)
    return render(request, 'donation_form.html')

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
            stream.is_active = False
            stream.save()
            return Response({'status': 'Stream stopped'}, status=status.HTTP_200_OK)
        except Stream.DoesNotExist:
            return Response({'error': 'Stream not found'}, status=status.HTTP_404_NOT_FOUND)


    def update(self, request, *args, **kwargs):
        stream = self.get_object()
        stream.is_active = True
        stream.save()
        return Response(StreamSerializer(stream).data)

class StreamVideoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        # try:
        #     stream = Stream.objects.get(pk=pk)
        #     video_url = f'/path/to/hls/{stream}.m3u8'
        #     return Response({'video_url': video_url})
        # except Stream.DoesNotExist:
        #     return Response({'error': 'Stream not found'}, status=status.HTTP_404_NOT_FOUND)
        
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

class StreamCommentsView(generics.ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        stream_id = self.kwargs['stream_id']
        return Comment.objects.filter(stream_id=stream_id).order_by('-created_at')

@csrf_exempt
def midtrans_notification(request):
    if request.method == 'POST':
        notification = json.loads(request.body)
        order_id = notification.get('order_id')
        transaction_status = notification.get('transaction_status')
        # Update your order status based on the notification
        return JsonResponse({'status': 'ok'})