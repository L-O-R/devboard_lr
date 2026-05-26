from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only = True, min_length = 8)
    password2 = serializers.CharField(write_only = True, min_length = 8)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2', 'role']

    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Password do not match!'})
        
        return attrs
    

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only = True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username = email,
            password = password,
        )


        if not user:
            raise serializers.ValidationError("Invalid Email or Password")
        
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled , Contact Admin to activate it!")
    
        attrs['user'] = user

        return attrs
    


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'role', 'bio',
            'profile_picture', 'date_joined'
        ]

        read_only_fields = ['id', 'email', 'role', 'date_joined']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only = True)
    new_password = serializers.CharField(write_only=True, min_length = 8)


    def validate(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("old password do not match")
        return value
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user