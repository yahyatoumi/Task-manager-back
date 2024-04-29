from django.shortcuts import render
from rest_framework import generics
from .models import CustomUser, Room, FavoritesRoomsList
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
import requests
from rest_framework.utils import json
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import RoomSerializer

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_rooms(request):
    user = request.user
    rooms = user.rooms.all()
    serializer = RoomSerializer(rooms, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def create_room(request):
    serializer = RoomSerializer(data=request.data)
    if serializer.is_valid():
        room = serializer.save(owner=request.user)
        room.add_member(request.user)
        return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def set_room_to_favorite(request):
    if "room_id" not in request.data:
        return Response({"error": "room_id field is required"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    try:
        room = Room.objects.get(pk=request.data["room_id"])
    except ObjectDoesNotExist:
        return Response({"error": "You are not in that room"}, status=status.HTTP_403_FORBIDDEN)
        
    user = request.user
    user_rooms = user.rooms.all()
    if room not in user_rooms:
        return Response({"error": "You are not in that room"}, status=status.HTTP_403_FORBIDDEN)
    favorites_rooms_list, _ = FavoritesRoomsList.objects.get_or_create(user=request.user)
    
    favorites_rooms_list.make_favorite(room)
        
    serializer = RoomSerializer(room, context={'request': request})
    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def set_room_to_not_favorite(request):
    if "room_id" not in request.data:
        return Response({"error": "room_id field is required"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    try:
        room = Room.objects.get(pk=request.data["room_id"])
    except ObjectDoesNotExist:
        return Response({"error": "You are not in that room"}, status=status.HTTP_403_FORBIDDEN)
        
    user = request.user
    user_rooms = user.rooms.all()
    if room not in user_rooms:
        return Response({"error": "You are not in that room"}, status=status.HTTP_403_FORBIDDEN)
    favorites_rooms_list, _ = FavoritesRoomsList.objects.get_or_create(user=request.user)
    
    favorites_rooms_list.make_not_favorite(room)

    serializer = RoomSerializer(room, context={'request': request})
    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

