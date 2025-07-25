from rest_framework import serializers
from .models import User

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