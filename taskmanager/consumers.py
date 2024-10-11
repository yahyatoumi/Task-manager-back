import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from .serializers import SectionSerializer, CustomUserSerializer, ProjectSerializer
from .models import Section, CustomUser, Task
from channels.db import database_sync_to_async       


class TextRoomConsumer(AsyncWebsocketConsumer):
    from .models import Project
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["board_id"]
        self.room_group_name = f"board_{self.room_name}"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        print("HERRRROOOOO", self.scope['url_route']['kwargs']['board_id'])
        user = self.scope.get('user')

        if user is None or isinstance(user, AnonymousUser):
            print("userrrr", user)
            self.close()
            return
        print("UUUUUUSR", user)
        
        project_pk = self.scope['url_route']['kwargs']['board_id']
        await self.user_in_project_check(project_pk, user)
        print("frrrrr")
        
        await self.accept()
        
        return await self.send(json.dumps({
                    "type": "websocket.accept"
                }))
    
    async def disconnect(self, close_code):
        # Leave room group
        await (self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Receive message from WebSocket
        text_data_json = json.loads(text_data)
        print("TEXT DATA JSON", text_data_json)
        project_id = self.scope['url_route']['kwargs']['board_id']
        await self.reorder_logic(text_data_json, project_id)
        await self.broadcast_order(project_id)
                    

    async def broadcast_order(self, project_id):
        print("brrroaasdddd")
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'section_update',
                "project_id": project_id
            }
        )
        
    async def section_update(self, event):
        print("event====="*32)
        print(event)
        # Send project to WebSocket
        project = await self.get_project_by_pk(event["project_id"])
        serializer = await self.serialize_project(project)
        response_data = {
            "type": "section_update",
            "project": serializer
        }
        await self.send(text_data=json.dumps(response_data))
        
    @database_sync_to_async
    def serialize_project(self, project):
        return ProjectSerializer(project).data
 
    @database_sync_to_async
    def get_user_by_pk(self, pk):
        return Project.objects.get(pk=pk)

    @database_sync_to_async
    def get_task_by_pk(self, pk):
        return Task.objects.get(pk=pk)
    
    @database_sync_to_async
    def get_project_by_pk(self, pk):
        return Project.objects.get(pk=pk)
    

    @database_sync_to_async
    def user_in_project_check(self, project_pk, user):
        user_projects = user.projects.all()
        project = Project.objects.get(pk=project_pk)
        if (project not in user_projects):
            raise Project.DoesNotExist
        
    @database_sync_to_async
    def reorder_logic(self, text_data_json, project_id):
        new_sections_order = text_data_json["sectionsIds"]
        print("TEXT DATA JSON", new_sections_order, len(new_sections_order), project_id)
        project = Project.objects.get(pk=self.scope['url_route']['kwargs']['board_id'])
        print("herrrrrooo")
        sections = project.sections.all()
        for section in sections:
            section_id_str = str(section.id)
            try:
                section_new_order = new_sections_order.index(section_id_str)
                section.update_order(section_new_order)
                print("seccc", section, section_new_order)
            except ValueError:
                pass
        tasks = text_data_json["tasks"]
        for task in tasks:
            taskObj = Task.objects.get(pk=task["taskId"])
            if project.id != taskObj.in_section.project_id:
                print("not same project", project, task.in_section.project)
                self.disconnect()
            print("iiii")
            taskObj.change_section(task["sectionId"])
            taskObj.change_order(task["order"])
        print("will broadcast")   

