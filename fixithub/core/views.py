from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    UserSerializer, CustomTokenObtainPairSerializer, HandymanProfileSerializer,
    JobRequestSerializer, ReviewSerializer, PaymentSerializer, JobAdSerializer,
    SMSLogSerializer, AdminSerializer
)
from .permissions import IsAdmin, IsHandyman, IsClient
from .models import HandymanProfile, JobRequest, Review, Payment, JobAd, SMSLog, Admin
import logging

logger = logging.getLogger(__name__)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class TestAuthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": f"Hello, {request.user.email}! Role: {request.user.role}"})

class AdminOnlyView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        return Response({"message": f"Welcome, {request.user.email}! This is an admin-only endpoint."})

class HandymanOnlyView(APIView):
    permission_classes = [IsAuthenticated, IsHandyman]

    def get(self, request):
        return Response({"message": f"Welcome, {request.user.email}! This is a handyman-only endpoint."})

class ClientOnlyView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def get(self, request):
        return Response({"message": f"Welcome, {request.user.email}! This is a client-only endpoint."})

class HandymanProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'handyman':
            profile = HandymanProfile.objects.filter(handyman=request.user).first()
            if not profile:
                return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = HandymanProfileSerializer(profile)
            return Response(serializer.data)
        return Response(HandymanProfileSerializer(HandymanProfile.objects.all(), many=True).data)

    def post(self, request):
        if request.user.role != 'handyman':
            return Response({"detail": "Only handyman users can create profiles"}, status=status.HTTP_403_FORBIDDEN)
        if HandymanProfile.objects.filter(handyman=request.user).exists():
            return Response({"detail": "Profile already exists"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = HandymanProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(handyman=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        if request.user.role != 'handyman':
            return Response({"detail": "Only handyman users can update profiles"}, status=status.HTTP_403_FORBIDDEN)
        profile = HandymanProfile.objects.filter(handyman=request.user).first()
        if not profile:
            return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = HandymanProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JobRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'client':
            jobs = JobRequest.objects.filter(client=request.user)
        elif request.user.role == 'handyman':
            jobs = JobRequest.objects.filter(handyman=request.user)
        elif request.user.role == 'admin':
            jobs = JobRequest.objects.all()
        else:
            return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        serializer = JobRequestSerializer(jobs, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role != 'client':
            return Response({"detail": "Only clients can create job requests"}, status=status.HTTP_403_FORBIDDEN)
        serializer = JobRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(client=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JobRequestAcceptView(APIView):
    permission_classes = [IsAuthenticated, IsHandyman]

    def post(self, request, job_id):
        try:
            job = JobRequest.objects.get(job_id=job_id, status='pending')
            if job.handyman:
                return Response({"detail": "Job already assigned"}, status=status.HTTP_400_BAD_REQUEST)
            job.handyman = request.user
            job.status = 'accepted'
            job.save()
            return Response(JobRequestSerializer(job).data)
        except JobRequest.DoesNotExist:
            return Response({"detail": "Job not found or not pending"}, status=status.HTTP_404_NOT_FOUND)

class ReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'handyman':
            reviews = Review.objects.filter(handyman=request.user)
        elif request.user.role == 'client':
            reviews = Review.objects.filter(client=request.user)
        elif request.user.role == 'admin':
            reviews = Review.objects.all()
        else:
            return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role != 'client':
            return Response({"detail": "Only clients can post reviews"}, status=status.HTTP_403_FORBIDDEN)
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            job = serializer.validated_data['job']
            if job.client != request.user or job.status != 'completed':
                return Response({"detail": "Invalid job or not completed"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(client=request.user, handyman=job.handyman)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'admin':
            payments = Payment.objects.all()
        else:
            payments = Payment.objects.filter(user=request.user)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JobAdView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ads = JobAd.objects.filter(is_active=True)
        serializer = JobAdSerializer(ads, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role != 'handyman':
            return Response({"detail": "Only handymen can create job ads"}, status=status.HTTP_403_FORBIDDEN)
        serializer = JobAdSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(handyman=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SMSLogView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        logs = SMSLog.objects.all()
        serializer = SMSLogSerializer(logs, many=True)
        return Response(serializer.data)

class AdminRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)