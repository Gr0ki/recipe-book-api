"""URL pappings for the recipe app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet


app_name = "recipe"

router = DefaultRouter()
router.register("", RecipeViewSet, basename="recipe")

urlpatterns = [path("", include(router.urls))]
