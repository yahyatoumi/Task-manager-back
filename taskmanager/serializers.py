from .models import Room, CustomUser, FavoritesRoomsList, Project, Section, Task
from rest_framework import serializers

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username']
        write_only_fields = ["password"]

class RoomSerializer(serializers.ModelSerializer):
    owner = CustomUserSerializer(read_only=True)
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
        owner = self.context['request'].user  # Get the authenticated user from the context
        room = Room.objects.create(owner=owner, **validated_data)
        room.add_member(owner)
        return room
            
    def validate(self, attrs):
        if "name" not in attrs:
            return serializers.ValidationError({"name": "name required"})

        return attrs
    

    
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"
    
class SectionSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    
    class Meta:
        model = Section
        fields = ['id', 'name', 'project', 'tasks']

    
class ProjectSerializer(serializers.ModelSerializer):
    room_id = serializers.IntegerField(write_only=True)
    created_by = CustomUserSerializer(read_only=True)
    members = CustomUserSerializer(many=True, read_only=True)
    
    class Meta(object):
        model = Project
        fields = ['id', 'name', 'room', 'room_id', 'created_by', 'members', 'date_created', 'color']
        read_only_fields = ['created_by', "room", 'members']
        
    def create(self, validated_data):
        print("CCCCR", validated_data)
        room = Room.objects.get(pk=validated_data["room_id"])
        created_by = self.context['request'].user
        validated_data.pop("room_id")
        project = Project.objects.create(room=room, created_by=created_by, **validated_data)
        project.add_member(created_by)
        # Create default sections
        Section.objects.create(project=project, name='To Do')
        Section.objects.create(project=project, name='In Progress')
        Section.objects.create(project=project, name='Done')
        return project
    
class TaskCreateSerializer(serializers.ModelSerializer):
    section_id = serializers.CharField(write_only=True)
    
    class Meta:
        model = Task
        fields = ["id", "name", "section_id"]
        
    def create(self, validated_data):
        section = Section.objects.get(pk=validated_data["section_id"])
        project = section.project
        created_by = self.context['request'].user
        print("created_by", created_by)
        print("project", project)
        print("members", project.members)
        if created_by not in project.members.all():
            raise serializers.ValidationError("You are not a member of the project.")
        validated_data.pop("section_id")
        task = Task.objects.create(in_section=section, created_by=created_by, **validated_data)
        return task