from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, CustomTokenObtainPairSerializer
from .permissions import IsAdmin, IsHandyman, IsClient

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