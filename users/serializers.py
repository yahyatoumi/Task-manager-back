from rest_framework import serializers
from users.models import CustomUser
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    def create(self, validated_data):

        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )

        return user
    
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