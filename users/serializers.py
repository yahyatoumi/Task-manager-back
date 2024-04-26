from rest_framework import serializers
from users.models import CustomUser
from django.contrib.auth.password_validation import validate_password
from django.utils.crypto import get_random_string

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'password2', 'email', ]
        extra_kwargs = {
            'username': {'required': True},
        }
        
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs
    
    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])
        user.save()

        return user
    
class GoogleUserSerializer(serializers.ModelSerializer):    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', "google_id"]
        extra_kwargs = {
            'email': {'required': True},
        }
        
    def validate(self, attrs):
        print("EMILLLL", attrs["email"])
        if CustomUser.objects.filter(email=attrs['email']).exists():
            return serializers.ValidationError({"email": "email already exists"})

        return attrs
    
    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            google_id=validated_data["google_id"]
        )
        user.set_password(get_random_string(20))
        user.save()

        return user