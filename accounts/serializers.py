from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(read_only=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email',
                  'first_name', 'last_name', 'is_staff', 'is_superuser')
        extra_kwargs = {
            'is_staff': {'read_only': False}
        }

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email',
                  'first_name', 'last_name')
        extra_kwargs = {
            'email': {'required': True, },
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"email": "A user with this email already exists."})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        is_staff = validated_data.pop('is_staff', False)

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=password
        )

        user.is_staff = is_staff
        user.save()

        return user
