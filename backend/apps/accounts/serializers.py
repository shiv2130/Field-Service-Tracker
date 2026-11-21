from .models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['name'] = user.name
        token['role'] = user.role

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'name': self.user.name,
            'phone': self.user.phone,
            'role': self.user.role
        }

        return data


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
       model = User
       fields = ['id', 'username', 'name', 'phone', 'role']