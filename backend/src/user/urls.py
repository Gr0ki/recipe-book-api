from django.urls import path

from .views import UserCreate, UserToken, ManageUserView


app_name = "user"

urlpatterns = [
    path("create/", UserCreate.as_view(), name="create"),
    path("token/", UserToken.as_view(), name="token"),
    path("me/", ManageUserView.as_view(), name="me"),
]
