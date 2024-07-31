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
    tasks = serializers.SerializerMethodField()
    
    class Meta:
        model = Section
        fields = ['id', 'name', 'project', 'tasks', "order_in_Project"]
        read_only_fields = ["order_in_Project"]

        
    def get_tasks(self, obj):
        print("ordereeeeddd")
        tasks = obj.tasks.order_by('order_in_section')
        return TaskSerializer(tasks, many=True).data

    
class ProjectSerializer(serializers.ModelSerializer):
    room_id = serializers.IntegerField(write_only=True)
    created_by = CustomUserSerializer(read_only=True)
    members = CustomUserSerializer(many=True, read_only=True)
    # sections = SectionSerializer(many=True, read_only=True)
    sections = serializers.SerializerMethodField()
    
    class Meta(object):
        model = Project
        fields = ['id', 'name', 'room', 'room_id', 'created_by', 'members', 'date_created', 'color', "sections"]
        read_only_fields = ['created_by', "room", 'members', 'sections']
        
    def get_sections(self, obj):
        print("ordereeeeddd sections")
        sections = obj.sections.order_by('order_in_Project')
        return SectionSerializer(sections, many=True).data
        
    def create(self, validated_data):
        print("CCCCR", validated_data)
        room = Room.objects.get(pk=validated_data["room_id"])
        created_by = self.context['request'].user
        validated_data.pop("room_id")
        project = Project.objects.create(room=room, created_by=created_by, **validated_data)
        project.add_member(created_by)
        # Create default sections
        Section.objects.create(project=project, name='To Do', order_in_Project=0)
        Section.objects.create(project=project, name='In Progress', order_in_Project=1)
        Section.objects.create(project=project, name='Done', order_in_Project=2)
        return project
    
class TaskCreateSerializer(serializers.ModelSerializer):
    section_id = serializers.CharField(write_only=True)
    
    class Meta:
        model = Task
        fields = ["id", "name", "section_id", "created_by", "date_created", "date_updated"]
        read_only_fields = ('id', 'created_by', 'date_created', 'date_updated')
        
    def create(self, validated_data):
        section = Section.objects.get(pk=validated_data["section_id"])
        project = section.project
        created_by = self.context['request'].user
        print("created_by", created_by)
        print("project", project)
        print("members", project.members)
        print("sec len", len(section.tasks.all()))
        if created_by not in project.members.all():
            raise serializers.ValidationError("You are not a member of the project.")
        validated_data.pop("section_id")
        task = Task.objects.create(in_section=section, created_by=created_by, order_in_section=len(section.tasks.all()), **validated_data)
        return task