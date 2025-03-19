from django.urls import path
from accounts.views import RegisterView, LoginView, UserDetailView, LogoutView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]
