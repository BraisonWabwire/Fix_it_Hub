from rest_framework import serializers
from .models import User, HandymanProfile, JobRequest, Review, Payment, JobAd, SMSLog, Admin
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import logging

logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=[('client', 'Client'), ('handyman', 'Handyman')], required=True)

    class Meta:
        model = User
        fields = ['user_id', 'full_name', 'email', 'phone', 'password', 'role', 'location', 'is_active']
        read_only_fields = ['user_id', 'is_active', 'created_at']

    def validate_role(self, value):
        if value not in ['client', 'handyman']:
            logger.error(f"Invalid role attempted: {value}")
            raise serializers.ValidationError("Role must be 'client' or 'handyman'.")
        return value

    def create(self, validated_data):
        logger.info(f"Creating user with email: {validated_data['email']}")
        user = User.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            phone=validated_data['phone'],
            password=validated_data['password'],
            role=validated_data['role'],
            location=validated_data.get('location', '')
        )
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class AdminUserSerializer(UserSerializer):
    password = serializers.CharField(write_only=True, required=True)
    role = serializers.CharField(default='admin', read_only=True)

    class Meta(UserSerializer.Meta):
        fields = ['user_id', 'full_name', 'email', 'phone', 'password', 'role', 'location', 'is_active']
        read_only_fields = ['user_id', 'is_active', 'created_at', 'role']

    def create(self, validated_data):
        validated_data['role'] = 'admin'
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = user.full_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'user_id': self.user.user_id,
            'email': self.user.email,
            'role': self.user.role,
            'full_name': self.user.full_name,
            'phone': self.user.phone,
            'location': self.user.location
        }
        return data

class HandymanProfileSerializer(serializers.ModelSerializer):
    handyman = UserSerializer(read_only=True)  # Include user details

    class Meta:
        model = HandymanProfile
        fields = [
            'handyman', 'category', 'experience_years', 'bio',
            'rating', 'jobs_completed', 'is_verified', 'subscription_plan'
        ]
        read_only_fields = ['handyman', 'rating', 'jobs_completed', 'is_verified']

class JobRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRequest
        fields = ['job_id', 'client', 'handyman', 'category', 'job_description', 'job_location', 'preferred_date', 'status', 'created_at', 'updated_at']
        read_only_fields = ['job_id', 'client', 'created_at', 'updated_at']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['review_id', 'job', 'client', 'handyman', 'rating', 'comment', 'created_at']
        read_only_fields = ['review_id', 'client', 'handyman', 'created_at']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['payment_id', 'user', 'amount', 'purpose', 'reference_code', 'payment_method', 'status', 'created_at']
        read_only_fields = ['payment_id', 'user', 'created_at']

class JobAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAd
        fields = ['ad_id', 'handyman', 'title', 'ad_description', 'image_url', 'is_active', 'start_date', 'end_date']
        read_only_fields = ['ad_id', 'handyman']

class SMSLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSLog
        fields = ['sms_id', 'user', 'message', 'phone', 'status', 'sent_at']
        read_only_fields = ['sms_id', 'user', 'sent_at']

class AdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Admin
        fields = ['admin_id', 'username', 'password', 'email']
        read_only_fields = ['admin_id']

    def create(self, validated_data):
        from django.contrib.auth.hashers import make_password
        validated_data['password_hash'] = make_password(validated_data.pop('password'))
        return Admin.objects.create(**validated_data)