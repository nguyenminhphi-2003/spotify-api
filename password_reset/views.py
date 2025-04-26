from django.contrib.auth.password_validation import validate_password
from mongoengine import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.core.mail import send_mail, get_connection
from django.conf import settings
import random
import string
from datetime import datetime, timedelta
from rest_framework.permissions import AllowAny
from .models import PasswordResetCode

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        print(f"Received email: {email}")  # Debug: In email nhận được
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Find user by email
        user = User.objects.filter(email=email).first()
        print(f"User found: {user}")  # Debug: Kiểm tra user
        if not user:
            return Response({'message': 'If this email exists, a reset code has been sent'}, status=status.HTTP_200_OK)

        # Generate a 6-digit code
        code = ''.join(random.choices(string.digits, k=6))
        print(f"Generated code: {code}")  # Debug: In mã code

        # Set expiration (1 hour)
        expires_at = datetime.now() + timedelta(hours=1)

        # Save the code to MongoDB
        try:
            reset_code = PasswordResetCode(
                user_id=str(user.id),
                code=code,
                expires_at=expires_at
            )
            reset_code.save()
            print("Reset code saved successfully")  # Debug: Xác nhận lưu MongoDB
        except Exception as e:
            print(f"MongoDB save error: {str(e)}")  # Debug: Lỗi MongoDB
            return Response({'error': f"Failed to save reset code: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Send email
        subject = 'Your Password Reset Code'
        message = f"""
Hello {user.username},

You requested a password reset for your Spotify Clone account.
Your password reset code is: {code}

This code will expire in 1 hour.

If you didn't request this, please ignore this email.

Regards,
The Spotify Clone Team
        """

        try:
            with get_connection() as connection:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                    connection=connection,
                )
            print("Email sent successfully")  # Debug: Xác nhận gửi email
        except Exception as e:
            print(f"Email sending error: {str(e)}")  # Debug: Lỗi gửi email
            return Response({'error': f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'Reset code sent successfully'}, status=status.HTTP_200_OK)

class PasswordResetVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        new_password = request.data.get('new_password')
        new_password2 = request.data.get('new_password2')

        # Validate input
        if not all([email, code, new_password, new_password2]):
            return Response({
                'error': 'Email, code, and new passwords are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        if new_password != new_password2:
            return Response({
                'error': 'Passwords do not match'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validate password
            validate_password(new_password)
        except ValidationError as e:
            return Response({
                'error': e.messages
            }, status=status.HTTP_400_BAD_REQUEST)

        # Find user
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({
                'error': 'Invalid email or code'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Find valid reset code
        now = datetime.now()
        reset_codes = PasswordResetCode.objects(
            user_id=str(user.id),
            code=code,
            is_used=False,
            expires_at__gt=now
        ).order_by('-created_at')

        if not reset_codes:
            return Response({
                'error': 'Invalid or expired code'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Mark code as used
        reset_code = reset_codes.first()
        reset_code.is_used = True
        reset_code.save()

        # Update password
        user.set_password(new_password)
        user.save()

        return Response({
            'message': 'Password has been reset successfully'
        }, status=status.HTTP_200_OK)