from django.urls import path
from .views import (
    RegisterView, TestAuthView, AdminOnlyView, HandymanOnlyView, ClientOnlyView,
    HandymanProfileView, JobRequestView, JobRequestAcceptView, ReviewView,
    PaymentView, JobAdView, SMSLogView, UserDetailView, BanUserView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('test-auth/', TestAuthView.as_view(), name='test-auth'),
    path('admin-only/', AdminOnlyView.as_view(), name='admin-only'),
    path('handyman-only/', HandymanOnlyView.as_view(), name='handyman-only'),
    path('client-only/', ClientOnlyView.as_view(), name='client-only'),
    path('handyman-profiles/', HandymanProfileView.as_view(), name='handyman-profiles'),
    path('job-requests/', JobRequestView.as_view(), name='job-requests'),
    path('job-requests/<int:job_id>/accept/', JobRequestAcceptView.as_view(), name='job-request-accept'),
    path('reviews/', ReviewView.as_view(), name='reviews'),
    path('payments/', PaymentView.as_view(), name='payments'),
    path('job-ads/', JobAdView.as_view(), name='job-ads'),
    path('sms-logs/', SMSLogView.as_view(), name='sms-logs'),
    path('users/', UserDetailView.as_view(), name='user-list'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:user_id>/ban/', BanUserView.as_view(), name='ban-user'),
]