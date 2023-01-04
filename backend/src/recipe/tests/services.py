from django.urls import reverse
from django.contrib.auth import get_user_model

from decimal import Decimal

from ..models import Recipe


RECIPE_LIST_URL = reverse("recipe:recipe-list")

USER_DEFAULTS = {"email": "test@example.com", "password": "testpass123S"}
RECIPE_DEFAULTS = {
    "title": "Test recipe name.",
    "time_minutes": 5,
    "price": Decimal("100.90"),
    "description": "Test description.",
}


def create_recipe_detail_url(recipe_id):
    return reverse("recipe:recipe-detail", args=(recipe_id,))


def create_user(**params):
    defaults = USER_DEFAULTS.copy()
    defaults.update(params)
    user = get_user_model().objects.create_user(**defaults)
    return user


def create_recipe(user, **params):
    defaults = RECIPE_DEFAULTS.copy()
    defaults.update(params)
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe
