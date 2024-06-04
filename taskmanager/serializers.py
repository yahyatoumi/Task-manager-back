from .models import Room, CustomUser, FavoritesRoomsList, Project
from rest_framework import serializers

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username']
        
class CreatRoomSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Room
        fields = ['id', 'name', 'description']
    

class RoomSerializer(serializers.ModelSerializer):
    owner = CustomUserSerializer()
    is_favorite = serializers.SerializerMethodField()
        
    class Meta(object):
        model = Room
        depth = 2
        fields = ['id', 'name', 'color', "owner", 'is_favorite', 'description']
        
    def get_is_favorite(self, room):
        user = self.context['request'].user
        favorite_rooms, _ = FavoritesRoomsList.objects.get_or_create(user=user)
        return favorite_rooms.is_favorite(room)
    
    def create(self, validated_data):
        print("CREATTTTTTT")
        owner_data = validated_data.pop('owner')
        owner = CustomUserSerializer.create(CustomUserSerializer(), validated_data=owner_data)
        room = Room.objects.create(owner=owner, **validated_data)
        return room
            
    def validate(self, attrs):
        if "name" not in attrs:
            return serializers.ValidationError({"name": "name required"})

        return attrs
    
class ProjectSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Project
        fields = "__all__"