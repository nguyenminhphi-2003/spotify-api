from django.urls import path
from .views import PasswordResetRequestView, PasswordResetVerifyView

urlpatterns = [
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/verify/', PasswordResetVerifyView.as_view(), name='password-reset-verify'),
]