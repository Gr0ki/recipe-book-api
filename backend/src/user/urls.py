from django.urls import path

from .views import UserCreate, UserToken


app_name = "user"

urlpatterns = [
    path("create/", UserCreate.as_view(), name="create"),
]
