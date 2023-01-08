"""URL pappings for the recipe app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, TagViewSet


app_name = "recipe"

router = DefaultRouter()
router.register("recipes", RecipeViewSet)
router.register("tags", TagViewSet)

urlpatterns = [path("", include(router.urls))]
