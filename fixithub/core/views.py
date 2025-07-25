from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    UserSerializer, CustomTokenObtainPairSerializer, HandymanProfileSerializer,
    JobRequestSerializer, ReviewSerializer, PaymentSerializer, JobAdSerializer,
    SMSLogSerializer, AdminUserSerializer
)
from .permissions import IsAdmin, IsHandyman, IsClient, IsOwnerOrAdmin
from .models import User, HandymanProfile, JobRequest, Review, Payment, JobAd, SMSLog
import logging

logger = logging.getLogger(__name__)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info(f"Register attempt: {request.data.get('email')}")
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"User registered: {serializer.data['email']}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Registration failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        logger.info(f"Login attempt: {request.data.get('email')}")
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            logger.info(f"Login successful: {request.data.get('email')}")
        else:
            logger.error(f"Login failed: {response.data}")
        return response

class TestAuthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(f"Test auth accessed by {request.user.email}")
        return Response({"message": f"Hello, {request.user.email}! Role: {request.user.role}"})

class AdminOnlyView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        logger.info(f"Admin-only endpoint accessed by {request.user.email}")
        return Response({"message": f"Welcome, {request.user.email}! This is an admin-only endpoint."})

class HandymanOnlyView(APIView):
    permission_classes = [IsAuthenticated, IsHandyman]

    def get(self, request):
        logger.info(f"Handyman-only endpoint accessed by {request.user.email}")
        return Response({"message": f"Welcome, {request.user.email}! This is a handyman-only endpoint."})

class ClientOnlyView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def get(self, request):
        logger.info(f"Client-only endpoint accessed by {request.user.email}")
        return Response({"message": f"Welcome, {request.user.email}! This is a client-only endpoint."})

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get(self, request, user_id=None):
        logger.info(f"GET user details by {request.user.email}, user_id={user_id}")
        if request.user.role == 'admin' and user_id:
            try:
                user = User.objects.get(user_id=user_id)
                serializer = AdminUserSerializer(user)
                return Response(serializer.data)
            except User.DoesNotExist:
                logger.error(f"User not found: user_id={user_id}")
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        elif request.user.role == 'admin':
            users = User.objects.all()
            serializer = AdminUserSerializer(users, many=True)
            return Response(serializer.data)
        else:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)

    def put(self, request, user_id=None):
        logger.info(f"PUT user details by {request.user.email}, user_id={user_id}")
        if request.user.role == 'admin' and user_id:
            try:
                user = User.objects.get(user_id=user_id)
                serializer = AdminUserSerializer(user, data=request.data, partial=True)
            except User.DoesNotExist:
                logger.error(f"User not found: user_id={user_id}")
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user
            serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            logger.info(f"User updated: {user.email}")
            return Response(serializer.data)
        logger.error(f"Update failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        if request.user.role != 'admin':
            logger.error(f"Delete attempt by non-admin: {request.user.email}")
            return Response({"detail": "Only admins can delete users"}, status=status.HTTP_403_FORBIDDEN)
        try:
            user = User.objects.get(user_id=user_id)
            user.delete()
            logger.info(f"User deleted: user_id={user_id} by {request.user.email}")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            logger.error(f"User not found: user_id={user_id}")
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class BanUserView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, user_id):
        logger.info(f"Ban attempt by {request.user.email} on user_id={user_id}")
        try:
            user = User.objects.get(user_id=user_id)
            if user.role == 'admin':
                logger.error(f"Attempt to ban admin user: {user.email}")
                return Response({"detail": "Cannot ban admin users"}, status=status.HTTP_403_FORBIDDEN)
            user.is_active = False
            user.save()
            logger.info(f"User banned: {user.email} by {request.user.email}")
            return Response({"message": f"User {user.email} has been banned"})
        except User.DoesNotExist:
            logger.error(f"User not found: user_id={user_id}")
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class HandymanProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(f"GET handyman profiles by {request.user.email}")
        if request.user.role == 'handyman':
            profile = HandymanProfile.objects.filter(handyman=request.user).first()
            if not profile:
                logger.error(f"Profile not found for handyman: {request.user.email}")
                return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = HandymanProfileSerializer(profile)
            return Response(serializer.data)
        return Response(HandymanProfileSerializer(HandymanProfile.objects.all(), many=True).data)

    def post(self, request):
        if request.user.role != 'handyman':
            logger.error(f"Profile creation attempt by non-handyman: {request.user.email}")
            return Response({"detail": "Only handyman users can create profiles"}, status=status.HTTP_403_FORBIDDEN)
        if HandymanProfile.objects.filter(handyman=request.user).exists():
            logger.error(f"Profile already exists for {request.user.email}")
            return Response({"detail": "Profile already exists"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = HandymanProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(handyman=request.user)
            logger.info(f"Profile created for {request.user.email}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Profile creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        if request.user.role != 'handyman':
            logger.error(f"Profile update attempt by non-handyman: {request.user.email}")
            return Response({"detail": "Only handyman users can update profiles"}, status=status.HTTP_403_FORBIDDEN)
        profile = HandymanProfile.objects.filter(handyman=request.user).first()
        if not profile:
            logger.error(f"Profile not found for handyman: {request.user.email}")
            return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = HandymanProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Profile updated for {request.user.email}")
            return Response(serializer.data)
        logger.error(f"Profile update failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JobRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(f"GET job requests by {request.user.email}")
        if request.user.role == 'client':
            jobs = JobRequest.objects.filter(client=request.user)
        elif request.user.role == 'handyman':
            jobs = JobRequest.objects.filter(handyman=request.user)
        elif request.user.role == 'admin':
            jobs = JobRequest.objects.all()
        else:
            logger.error(f"Permission denied for {request.user.email}")
            return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        serializer = JobRequestSerializer(jobs, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role != 'client':
            logger.error(f"Job request creation attempt by non-client: {request.user.email}")
            return Response({"detail": "Only clients can create job requests"}, status=status.HTTP_403_FORBIDDEN)
        serializer = JobRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(client=request.user)
            logger.info(f"Job request created by {request.user.email}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Job request creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JobRequestAcceptView(APIView):
    permission_classes = [IsAuthenticated, IsHandyman]

    def post(self, request, job_id):
        logger.info(f"Job accept attempt by {request.user.email} for job_id={job_id}")
        try:
            job = JobRequest.objects.get(job_id=job_id, status='pending')
            if job.handyman:
                logger.error(f"Job already assigned: job_id={job_id}")
                return Response({"detail": "Job already assigned"}, status=status.HTTP_400_BAD_REQUEST)
            job.handyman = request.user
            job.status = 'accepted'
            job.save()
            logger.info(f"Job accepted: job_id={job_id} by {request.user.email}")
            return Response(JobRequestSerializer(job).data)
        except JobRequest.DoesNotExist:
            logger.error(f"Job not found or not pending: job_id={job_id}")
            return Response({"detail": "Job not found or not pending"}, status=status.HTTP_404_NOT_FOUND)

class ReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(f"GET reviews by {request.user.email}")
        if request.user.role == 'handyman':
            reviews = Review.objects.filter(handyman=request.user)
        elif request.user.role == 'client':
            reviews = Review.objects.filter(client=request.user)
        elif request.user.role == 'admin':
            reviews = Review.objects.all()
        else:
            logger.error(f"Permission denied for {request.user.email}")
            return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role != 'client':
            logger.error(f"Review creation attempt by non-client: {request.user.email}")
            return Response({"detail": "Only clients can post reviews"}, status=status.HTTP_403_FORBIDDEN)
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            job = serializer.validated_data['job']
            if job.client != request.user or job.status != 'completed':
                logger.error(f"Invalid job or not completed: job_id={job.job_id}")
                return Response({"detail": "Invalid job or not completed"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(client=request.user, handyman=job.handyman)
            logger.info(f"Review created by {request.user.email} for job_id={job.job_id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Review creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(f"GET payments by {request.user.email}")
        if request.user.role == 'admin':
            payments = Payment.objects.all()
        else:
            payments = Payment.objects.filter(user=request.user)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

    def post(self, request):
        logger.info(f"Payment creation attempt by {request.user.email}")
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            logger.info(f"Payment created by {request.user.email}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Payment creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JobAdView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(f"GET job ads by {request.user.email}")
        ads = JobAd.objects.filter(is_active=True)
        serializer = JobAdSerializer(ads, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role != 'handyman':
            logger.error(f"Job ad creation attempt by non-handyman: {request.user.email}")
            return Response({"detail": "Only handymen can create job ads"}, status=status.HTTP_403_FORBIDDEN)
        serializer = JobAdSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(handyman=request.user)
            logger.info(f"Job ad created by {request.user.email}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Job ad creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SMSLogView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        logger.info(f"GET SMS logs by {request.user.email}")
        logs = SMSLog.objects.all()
        serializer = SMSLogSerializer(logs, many=True)
        return Response(serializer.data)