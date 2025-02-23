from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.throttling import AnonRateThrottle

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['phone_number'] = user.profile.phone_number if hasattr(user, 'profile') else None
        return token

    def validate(self, attrs):
        try:
            user = User.objects.get(username=attrs['username'])
            if not user.check_password(attrs['password']):
                raise exceptions.AuthenticationFailed('Invalid credentials')
                
            if not user.is_active:
                raise exceptions.AuthenticationFailed('User account disabled')
                
            return super().validate(attrs)
        except ObjectDoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')

class LoginThrottle(AnonRateThrottle):
    rate = '5/hour'

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [LoginThrottle]