from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from streaming.views import RegisterView, create_donation, ConfirmDonationView, CreateCommentView, StreamCommentsView, index
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="API documentation for Livestream",
        terms_of_service="https://www.google.com/policies/terms/",
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    #  permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('api/', include('streaming.urls')),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/donations/create/', create_donation, name='create_donation'),
    path('api/donations/<int:id>/confirm/', ConfirmDonationView.as_view(), name='confirm_donation'),
    path('api/comments/create/', CreateCommentView.as_view(), name='create_comment'),
    path('api/comments/<int:stream_id>/', StreamCommentsView.as_view(), name='stream_comments'),
    path('swagger/',  schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

