# streaming/urls.py

from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, CreateStreamView, StartStreamView, StopStreamView, ConfirmDonationView, CreateCommentView, StreamCommentsView, StreamVideoView, custom_login, donate, midtrans_notification
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings


schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="API documentation for Livestream",
        terms_of_service="https://www.google.com/policies/terms/",
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('streams/create/', CreateStreamView.as_view(), name='create_stream'),
    path('streams/<int:pk>/start/', StartStreamView.as_view(), name='start_stream'),
    path('streams/<int:pk>/stop/', StopStreamView.as_view(), name='stop_stream'),
    path('streams/<int:pk>/video/', StreamVideoView.as_view(), name='stream_video'),
    path('donations/<int:id>/confirm/', ConfirmDonationView.as_view(), name='confirm_donation'),
    path('comments/create/', CreateCommentView.as_view(), name='create_comment'),
    path('comments/<int:stream_id>/', StreamCommentsView.as_view(), name='stream_comments'),
    path('donate/', donate, name='donate'),
    path('accounts/login/', custom_login, name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('midtrans-notification/', midtrans_notification, name='midtrans_notification'),
    path('swagger/',  schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('django-rq/', include('django_rq.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.HLS_URL, document_root=settings.HLS_ROOT)