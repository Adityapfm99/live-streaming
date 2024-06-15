# streaming/views.py

from django.contrib.auth.models import User
from django.shortcuts import render,redirect
from httpcore import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import generics,status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer, DonationSerializer, CommentSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import Donation, Comment, Stream
from .serializers import UserSerializer, StreamSerializer, DonationSerializer, CommentSerializer
from .tasks import process_donation
from .models import Donation
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
            stream.is_active = True
            stream.save()
            return Response({'status': 'Stream started'}, status=status.HTTP_200_OK)
        except Stream.DoesNotExist:
            return Response({'error': 'Stream not found'}, status=status.HTTP_404_NOT_FOUND)

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


class CreateStreamView(generics.CreateAPIView):
    queryset = Stream.objects.all()
    serializer_class = StreamSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        donation = serializer.save()
        # Trigger the Celery task
        process_donation.delay(donation.id)

    def update(self, request, *args, **kwargs):
        stream = self.get_object()
        stream.is_active = True
        stream.save()
        return Response(StreamSerializer(stream).data)

class StreamVideoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            stream = Stream.objects.get(pk=pk)
            video_url = f"http://your.streaming.server/stream/{stream.id}/video.m3u8"
            return JsonResponse({'video_url': video_url})
        except Stream.DoesNotExist:
            return JsonResponse({'error': 'Stream not found'}, status=404)

class CreateStreamView(generics.CreateAPIView):
    queryset = Stream.objects.all()
    serializer_class = StreamSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class StreamCommentsView(generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        stream_id = self.kwargs['stream_id']
        return Comment.objects.filter(stream_id=stream_id)

@csrf_exempt
def midtrans_notification(request):
    if request.method == 'POST':
        notification = json.loads(request.body)
        order_id = notification.get('order_id')
        transaction_status = notification.get('transaction_status')
        # Update your order status based on the notification
        return JsonResponse({'status': 'ok'})