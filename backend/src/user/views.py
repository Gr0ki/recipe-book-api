from rest_framework.generics import CreateAPIView

from .serializers import UserSerializer


class UserCreate(CreateAPIView):
    serializer_class = UserSerializer
