import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chatroom.models import *


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = f"room_{self.scope['url_route']['kwargs']['room_name']}"
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name, 
            self.channel_name)
        
        await self.accept()
        
    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_name, 
            self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = text_data_json['sender']
        time = text_data_json["time"]

        await self.channel_layer.group_send(
            self.room_group_name,

        {
            'type': 'send_message',
            'message': message,
            'sender': sender,
            'time': time
        }
    )

    async def send_message(self, event):
        message = event['message']
        sender = event['sender']
        time = event['time']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'time': time

        }))

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        await self.channel_layer.group_send( self.room_group_name,
        {
            'type': 'chat_message',
            'message': message,
            'sender': self.scope['user'].username,
        }
    ) 

    @database_sync_to_async
    def create_message(self, data):

        get_room_by_name = Room.objects.get(room_name=data['room_name'])
        
        if not Message.objects.filter(message=data['message']).exists():
            new_message = Message(room=get_room_by_name, sender=data['sender'], message=data['message'])
            new_message.save()  

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
    }))  