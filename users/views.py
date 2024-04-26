from django.shortcuts import render
from .serializers import UserSerializer, GoogleUserSerializer
from rest_framework import generics
from .models import CustomUser
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
import requests
from rest_framework.utils import json
from .helpers import generate_random_username

@api_view(['POST'])
@parser_classes([MultiPartParser])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        response_data = {
            'user': {  # Include user information here
                'id': user.id,
                'username': user.username,
                'email': user.email
                # Add other user fields as needed
            },
            'access': access_token,
            'refresh': str(refresh)
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    if 'username' not in request.data or 'password' not in request.data:
        return Response({
            "username": ["username required"],
            "password":  ["password required"]
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    username = request.data["username"]
    try:
        user = CustomUser.objects.get(username=username)
    except ObjectDoesNotExist:
        return Response({
            "username":  ["invalid password"],
            "password":  ["invalid password"]
            }, status=status.HTTP_400_BAD_REQUEST) 
    password = request.data["password"]
    if not user.check_password(password):
        return Response({
            "password":  ["invalid password"]
            }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = UserSerializer(user)
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    response_data = {
            'user': serializer.data,
            'access': access_token,
            'refresh': str(refresh)
        }
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def google_auth(request):
    if "access_token" not in request.data:
        return Response({"error": "google access_token is required"})
    access_token = request.data['access_token']
    payload = {'access_token': access_token}
    r = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", 
                     headers={
                       'Authorization': "Bearer " + access_token 
                     },
                     params=payload
                     )
    if (r.status_code != 200):
        return Response(json.loads(r.text), status=status.HTTP_400_BAD_REQUEST)
    data = json.loads(r.text)
    try:
        print("IDDDD", data["id"])
        user = CustomUser.objects.get(google_id=data["id"])
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        response_data = {
            'user': {  # Include user information here
                'id': user.id,
                'username': user.username,
                'email': user.email
                # Add other user fields as needed
            },
            'access': access_token,
            'refresh': str(refresh)
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    except ObjectDoesNotExist:
        pass
    print("CREATIN NEW")
    lower_name = data["name"].lower()
    serializer_data = {
        "username": generate_random_username(lower_name),
        "email": data["email"],
        "google_id": data["id"]
    }
    serializer = GoogleUserSerializer(data=serializer_data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        response_data = {
            'user': {  # Include user information here
                'id': user.id,
                'username': user.username,
                'email': user.email
                # Add other user fields as needed
            },
            'access': access_token,
            'refresh': str(refresh)
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
