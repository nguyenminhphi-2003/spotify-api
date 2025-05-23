from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from chat.models import Chat, Message
from django.contrib.auth.models import User
from rest_framework_mongoengine import viewsets
from rest_framework_mongoengine.serializers import DocumentSerializer


class ChatSerializer(DocumentSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'sender', 'receiver', 'created_at']


class MessageSerializer(DocumentSerializer):
    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'content', 'timestamp']


class ChatListView(APIView):
    """List all chats for the current user"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = str(request.user.id)
        chats = Chat.objects(
            (Chat.sender == user_id) | (Chat.receiver == user_id)
        ).order_by('-created_at')
        result = []
        for chat in chats:
            other_user_id = chat.receiver if chat.sender == user_id else chat.sender
            last_message = Message.objects(
                chat=chat).order_by('-timestamp').first()
            chat_data = {
                'id': str(chat.id),
                'other_user_id': other_user_id,
                'created_at': chat.created_at.isoformat(),
            }
            if last_message:
                chat_data['last_message'] = {
                    'content': last_message.content,
                    'sender': last_message.sender,
                    'timestamp': last_message.timestamp.isoformat()
                }
            result.append(chat_data)

        return Response(result)


class ChatDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id):
        user_id = str(request.user.id)

        try:
            chat = Chat.objects.get(id=chat_id)
            if chat.sender != user_id and chat.receiver != user_id:
                return Response(
                    {"detail": "You do not have permission to view this chat"},
                    status=status.HTTP_403_FORBIDDEN
                )
            messages = Message.objects(chat=chat).order_by('timestamp')
            result = {
                'chat_id': str(chat.id),
                'participants': [chat.sender, chat.receiver],
                'messages': []
            }
            for msg in messages:
                result['messages'].append({
                    'id': str(msg.id),
                    'sender': msg.sender,
                    'content': msg.content,
                    'timestamp': msg.timestamp.isoformat()
                })
            return Response(result)
        except Chat.DoesNotExist:
            return Response(
                {"detail": "Chat not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class GetMyMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = str(request.user.id)
        messages = Message.objects(sender=user_id).order_by('timestamp')
        result = []
        for message in messages:
            try:
                chat = message.chat
                result.append({
                    'id': str(message.id),
                    'chat_id': str(chat.id),
                    'content': message.content,
                    'timestamp': message.timestamp.isoformat()
                })
            except Exception as e:
                continue

        return Response(result)


class ChatCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sender_id = str(request.user.id)
        receiver_id = request.data.get('receiver_id')

        if not receiver_id:
            return Response(
                {"detail": "receiver_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            receiver_id = str(receiver_id)  # Chuyển thành chuỗi
            # Kiểm tra xem receiver_id có tồn tại
            if not User.objects.filter(id=int(receiver_id)).exists():
                return Response(
                    {"detail": "Receiver does not exist"},
                    status=status.HTTP_404_NOT_FOUND
                )

            chat = Chat.get_or_create_chat(sender_id, receiver_id)
            serializer = ChatSerializer(chat)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error creating chat: {str(e)}")  # Ghi log để debug
            return Response(
                {"detail": f"Failed to create chat: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MessageCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, chat_id):
        try:
            chat = Chat.objects.get(id=chat_id)
            if chat.sender != str(request.user.id) and chat.receiver != str(request.user.id):
                return Response(
                    {"detail": "You do not have permission to send messages in this chat"},
                    status=status.HTTP_403_FORBIDDEN
                )
            message = Message(
                chat=chat,
                sender=str(request.user.id),
                content=request.data.get('content')
            )
            message.save()
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Chat.DoesNotExist:
            return Response(
                {"detail": "Chat not found"},
                status=status.HTTP_404_NOT_FOUND
            )