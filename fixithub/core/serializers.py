from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['user_id', 'full_name', 'email', 'phone', 'password', 'role', 'location']
        read_only_fields = ['user_id', 'created_at']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            phone=validated_data['phone'],
            password=validated_data['password'],
            role=validated_data.get('role', 'client'),
            location=validated_data.get('location', '')
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims to the token payload
        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = user.full_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add user details to the response
        data['user'] = {
            'user_id': self.user.user_id,
            'email': self.user.email,
            'role': self.user.role,
            'full_name': self.user.full_name,
            'phone': self.user.phone,
            'location': self.user.location
        }
        return data