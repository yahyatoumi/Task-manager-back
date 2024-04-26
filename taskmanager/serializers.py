from .models import Room, CustomUser
from rest_framework import serializers

class RoomSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Room
        fields = ['id', 'name']
        
        
    def validate(self, attrs):
        if "name" not in attrs:
            return serializers.ValidationError({"name": "name required"})

        return attrs