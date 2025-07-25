from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from core.views import RegisterView, CustomTokenObtainPairView

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('core.urls')),
]