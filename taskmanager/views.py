from django.shortcuts import render
from rest_framework import generics
from .models import CustomUser, Room, FavoritesRoomsList, Project, Section
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
from .serializers import RoomSerializer, CustomUserSerializer, ProjectSerializer, SectionSerializer, TaskCreateSerializer

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_rooms(request):
    user = request.user
    rooms = user.rooms.all()
    serializer = RoomSerializer(rooms, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def room(request, id):
    try:
        room = Room.objects.get(pk=id)
    except Room.DoesNotExist:
        return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = RoomSerializer(room, context={'request': request})
    response_data = serializer.data
    response_data["members"] = CustomUserSerializer(room.members.all(), many=True).data
    projects = Project.objects.filter(room=room)
    response_data["projects"] = ProjectSerializer(projects, many=True).data
    return Response(response_data, status=status.HTTP_200_OK)
    
    
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, JSONParser])
def create_room(request):
    serializer = RoomSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, JSONParser])
def set_room_to_favorite(request):
    print("in set_room_to_favorite")
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
@parser_classes([MultiPartParser, JSONParser])
def set_room_to_not_favorite(request):
    print("in set_room_to_not_favorite")
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


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, JSONParser])
def create_project(request):
    if ("room_id" not in request.data or "project_title" not in request.data):
        return Response("room_id and project_title required", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    room_id = request.data["room_id"]
    try:
        room = Room.objects.get(pk=room_id)
    except:
        return Response("Object not found", status=status.HTTP_404_NOT_FOUND)
    
    if (request.user not in room.members.all()):
        return Response("Object not found hhhh", status=status.HTTP_404_NOT_FOUND)
    
    color = "#333333"
    if ("color" in request.data):
        color = request.data["color"]
    
    project_data = {
        'name': request.data["project_title"],
        'room_id': request.data["room_id"],
        'color': color
    }
    print("codadaaa", project_data)
    
    serializer = ProjectSerializer(data=project_data, context={'request': request})
    if (serializer.is_valid()):
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, JSONParser])
def get_project(request, id):
    try:
        project = Project.objects.get(pk=id)
    except Project.DoesNotExist:
        return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
    
    members = project.members.all()
    if (request.user not in members):
        return Response({"error": "Project not found 2"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProjectSerializer(project, context={'request': request})
    sections = Section.objects.filter(project=project).prefetch_related('tasks')
    print("SSSSS", sections)
    response_data = serializer.data
    response_data["sections"] = SectionSerializer(sections, many=True).data
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, JSONParser])
def get_projects_in_workspace(request, id):
    try:
        workspace = Room.objects.get(pk=id)
    except Room.DoesNotExist or request.user not in Room.members.all():
        return Response({"error": "Workspace not found"}, status=status.HTTP_404_NOT_FOUND)
    
    projects = Project.objects.filter(room=workspace)

    serializer = ProjectSerializer(projects, many=True, context={'request': request})
    response_data = serializer.data
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, JSONParser])
def create_task(request):
    print("dddata", request.data)
    serializer = TaskCreateSerializer(data=request.data, context={'request': request})
    if (serializer.is_valid()):
        serializer.save()
        response_data = serializer.data
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=400)
    

