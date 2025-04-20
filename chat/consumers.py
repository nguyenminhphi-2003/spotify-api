import json
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import Chat, Message
import datetime


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.chat_with_id = self.scope['url_route']['kwargs']['chat_id']

        user_ids = sorted([self.user_id, self.chat_with_id])
        self.room_group_name = f'chat_{user_ids[0]}_{user_ids[1]}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data['message']
        
        sender_id = self.user_id
        receiver_id = self.chat_with_id
        
        chat = Chat.get_or_create_chat(sender_id, receiver_id)
        
        message = Message(
            chat=chat,
            sender=sender_id,
            content=message_content
        )
        message.save()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'sender': sender_id,
                'chat_id': str(chat.id),
                'timestamp': datetime.datetime.now().isoformat()
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'chat_id': event['chat_id'],
            'timestamp': event['timestamp']
        }))