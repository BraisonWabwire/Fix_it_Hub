from django.urls import path
from .views import TestAuthView, AdminOnlyView, HandymanOnlyView, ClientOnlyView

urlpatterns = [
    path('test-auth/', TestAuthView.as_view(), name='test-auth'),
    path('admin-only/', AdminOnlyView.as_view(), name='admin-only'),
    path('handyman-only/', HandymanOnlyView.as_view(), name='handyman-only'),
     path('client-only/', ClientOnlyView.as_view(), name='client-only'),
]