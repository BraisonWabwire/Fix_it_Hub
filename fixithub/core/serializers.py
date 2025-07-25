from rest_framework import serializers
from .models import User, HandymanProfile, JobRequest, Review, Payment, JobAd, SMSLog, Admin
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['user_id', 'full_name', 'email', 'phone', 'password', 'role', 'location', 'is_active']
        read_only_fields = ['user_id', 'created_at']
        extra_kwargs = {
            'role': {'read_only': True},  # Clients can't change role
            'is_active': {'read_only': True}  # Clients can't change is_active
        }

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

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class AdminUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def update(self, instance, validated_data):
        # Admins can update all fields, including role and is_active
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
    class Meta:
        model = HandymanProfile
        fields = ['handyman', 'category', 'experience_years', 'bio', 'rating', 'jobs_completed', 'is_verified', 'subscription_plan']
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