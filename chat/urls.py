from django.urls import path
from chat.views import ChatListView, ChatDetailView, GetMyMessagesView

urlpatterns = [
    path('', ChatListView.as_view(), name='chat-list'),
    path('<str:chat_id>/', ChatDetailView.as_view(), name='chat-detail'),
    path('messages/my/', GetMyMessagesView.as_view(), name='my-messages'),
]