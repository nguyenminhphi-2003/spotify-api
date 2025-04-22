from mongoengine import Document, StringField, DateTimeField, ReferenceField, ListField
import datetime


class Chat(Document):
    sender = StringField(required=True)
    receiver = StringField(required=True)
    created_at = DateTimeField(default=datetime.datetime.now)

    meta = {
        'collection': 'chats',
        'indexes': ['sender', 'receiver', 'created_at'],
        'ordering': ['-created_at']
    }

    @classmethod
    def get_or_create_chat(cls, sender_id, receiver_id):
        # Chuyển cả hai ID thành chuỗi
        sender_id = str(sender_id)
        receiver_id = str(receiver_id)

        # Sắp xếp để đảm bảo tính nhất quán
        user_ids = sorted([sender_id, receiver_id])

        # Tìm chat hiện có
        chat = cls.objects(
            sender=user_ids[0],
            receiver=user_ids[1]
        ).first()

        if not chat:
            chat = cls(sender=user_ids[0], receiver=user_ids[1])
            chat.save()

        return chat

class Message(Document):
    """
    Represents an individual message within a chat.
    """
    chat = ReferenceField('Chat', required=True) 
    sender = StringField(required=True)
    content = StringField(required=True) 
    timestamp = DateTimeField(default=datetime.datetime.now)
    
    meta = {
        'collection': 'messages',
        'indexes': [
            'chat',
            'sender',
            'timestamp'
        ],
        'ordering': ['timestamp']
    }