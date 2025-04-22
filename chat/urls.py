from django.urls import path
from chat.views import ChatListView, ChatDetailView, GetMyMessagesView, ChatCreateView, MessageCreateView

urlpatterns = [
    path('', ChatListView.as_view(), name='chat-list'),
    path('<str:chat_id>/messages/', MessageCreateView.as_view(), name='message-create'),
    path('create/', ChatCreateView.as_view(), name='chat-create'),
    path('<str:chat_id>/', ChatDetailView.as_view(), name='chat-detail'),
    path('messages/my/', GetMyMessagesView.as_view(), name='my-messages'),

]