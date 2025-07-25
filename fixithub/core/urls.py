from django.urls import path
from core.views import TestAuthView

urlpatterns = [
    path('test-auth/', TestAuthView.as_view(), name='test-auth'),
]