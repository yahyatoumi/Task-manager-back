import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Project
from django.contrib.auth.models import AnonymousUser
from .serializers import SectionSerializer, CustomUserSerializer
from .models import Section, CustomUser

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
        text = text_data_json['text']
        sender = text_data_json['sender']
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': text,
                'sender': sender
            }
        )

    def chat_message(self, event):
        # Receive message from room group
        text = event['message']
        sender = event['sender']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'text': text,
            'sender': sender
        }))