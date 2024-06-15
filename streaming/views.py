# streaming/views.py

from django.contrib.auth.models import User
from django.shortcuts import render
from httpcore import Response
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer, DonationSerializer, CommentSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import Donation, Comment, Stream
from .serializers import UserSerializer, StreamSerializer, DonationSerializer, CommentSerializer
from .tasks import process_donation

def index(request):
    return render(request, 'index.html')

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

class StopStreamView(generics.UpdateAPIView):
    queryset = Stream.objects.all()
    serializer_class = StreamSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        stream = self.get_object()
        stream.is_active = False
        stream.save()
        return Response(StreamSerializer(stream).data)

class CreateDonationView(generics.CreateAPIView):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [IsAuthenticated]

class StartStreamView(generics.UpdateAPIView):
    queryset = Stream.objects.all()
    serializer_class = StreamSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        stream = self.get_object()
        stream.is_active = True
        stream.save()
        return Response(StreamSerializer(stream).data)

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

