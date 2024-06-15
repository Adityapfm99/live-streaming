# streaming/urls.py

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, CreateStreamView, StartStreamView, StopStreamView, ConfirmDonationView, CreateCommentView, StreamCommentsView, StreamVideoView, create_donation, midtrans_notification

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('streams/create/', CreateStreamView.as_view(), name='create_stream'),
    path('streams/<int:pk>/video/', StreamVideoView.as_view(), name='stream_video'),
    path('streams/<int:id>/stop/', StopStreamView.as_view(), name='stop_stream'),
    path('donations/create/', create_donation, name='create_donation'),
    path('donations/<int:id>/confirm/', ConfirmDonationView.as_view(), name='confirm_donation'),
    path('comments/create/', CreateCommentView.as_view(), name='create_comment'),
    path('comments/<int:stream_id>/', StreamCommentsView.as_view(), name='stream_comments'),
    path('midtrans/notification/', midtrans_notification, name='midtrans_notification'),
]
