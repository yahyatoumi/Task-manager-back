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
import environ
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
# reading .env file
environ.Env.read_env()

# False if not in os.environ
DEBUG = env('DEBUG')
GOOGLE_CLIENT_ID = env('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = env('GOOGLE_CLIENT_SECRET')


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

@api_view(['GET'])
def auth(request):
    client_id = GOOGLE_CLIENT_ID
    redirect_uri = 'http://localhost:3000/login/googleAuth'
    scope = 'openid profile email'
    response_type = 'code'
    
    google_auth_url = f'https://accounts.google.com/o/oauth2/auth?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&response_type={response_type}'
    return Response(google_auth_url, status=status.HTTP_200_OK)


@api_view(['POST'])
def google_auth(request):
    if "code" not in request.data:
        return Response({"error": "google code is required"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    # return Response(request.data, status=200)
    code = request.data["code"]
    request_body = {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": 'http://localhost:3000/login/googleAuth',
                "code": code,
                "grant_type": 'authorization_code'
    }
    r = requests.post("https://oauth2.googleapis.com/token", json=request_body)
    if r.status_code != 200:
        return Response(r, status=r.status_code)
    data = json.loads(r.text)
    access_token = data['access_token']
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

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    user = request.user
    rooms = user.rooms.all()
    serializer = RoomSerializer(rooms, many=True, context={'request': request})
    return Response(serializer.data)
