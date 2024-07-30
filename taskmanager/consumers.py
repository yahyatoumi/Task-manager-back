import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Project
from django.contrib.auth.models import AnonymousUser
from .serializers import SectionSerializer, CustomUserSerializer
from .models import Section, CustomUser, Project

class TextRoomConsumer(WebsocketConsumer):
    def connect(self):
        print("HERRRROOOOO", self.scope['url_route']['kwargs']['board_id'])
        user = self.scope.get('user')

        if user is None or isinstance(user, AnonymousUser):
            print("userrrr", user)
            self.close()
            return
        print("UUUUUUSR", user)
        
        try:
            project = Project.objects.get(pk=self.scope['url_route']['kwargs']['board_id'])
            if user not in project.members.all():
                raise Project.DoesNotExist
        except Project.DoesNotExist:
            self.close()
            return 
        
        self.accept()
        sections = Section.objects.filter(project=project)
        
        return self.send(json.dumps({
                    "type": "websocket.accept",
                    "send": CustomUserSerializer(user).data,
                    "sections": SectionSerializer(sections, many=True).data
                }))
    
    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        # Receive message from WebSocket
        text_data_json = json.loads(text_data)
        print("TEXT DATA JSON", text_data_json)
        project_id = self.scope['url_route']['kwargs']['board_id']
        new_sections_order = text_data_json["sectionsIds"]
        print("TEXT DATA JSON", new_sections_order, len(new_sections_order), project_id)
        project = Project.objects.get(pk=self.scope['url_route']['kwargs']['board_id'])
        sections = project.sections.all()
        for section in sections:
            section_id_str = str(section.id)
            try:
                section_new_order = new_sections_order.index(section_id_str)
                section.update_order(section_new_order)
                print("seccc", section, section_new_order)
            except ValueError:
                pass
        

    def broadcast_order(self, section_ids):
        self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'section_update',
                'message': {'sectionsIds': section_ids}
            }
        )

    def chat_message(self, event):
        # Receive message from room group
        print("EVENT", event)
        text = event['message']
        sender = event['sender']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'text': text,
            'sender': sender
        }))