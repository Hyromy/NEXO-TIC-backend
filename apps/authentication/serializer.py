from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)
        cls._add_user_data(token, user)
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        self._add_user_data(data, self.user)
        return data
    
    @staticmethod
    def _add_user_data(container, user: User):
        container["is_staff"] = user.is_staff
        container["is_superuser"] = user.is_superuser
        container["username"] = user.username
        container["first_name"] = user.first_name
        container["last_name"] = user.last_name
