from .models import Room, CustomUser, FavoritesRoomsList
from rest_framework import serializers

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username']

class RoomSerializer(serializers.ModelSerializer):
    owner = CustomUserSerializer()
    is_favorite = serializers.SerializerMethodField()
        
    class Meta(object):
        model = Room
        depth = 2
        fields = ['id', 'name', 'color', "owner", 'is_favorite']
        
    def get_is_favorite(self, room):
        user = self.context['request'].user
        favorite_rooms, _ = FavoritesRoomsList.objects.get_or_create(user=user)
        return favorite_rooms.is_favorite(room)
            
        
    def validate(self, attrs):
        if "name" not in attrs:
            return serializers.ValidationError({"name": "name required"})

        return attrs