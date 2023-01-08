from django.urls import reverse
from django.contrib.auth import get_user_model

from decimal import Decimal

from ..models import Recipe, Tag


RECIPE_LIST_URL = reverse("recipe:recipe-list")
TAG_LIST_URL = reverse("recipe:tag-list")

USER_DEFAULTS = {"email": "test@example.com", "password": "testpass123S"}
RECIPE_DEFAULTS = {
    "title": "Test recipe name.",
    "time_minutes": 5,
    "price": Decimal("100.90"),
    "description": "Test description.",
}
TAG_DEFAULTS = {
    "name": "Test-tag",
}


def create_tag_detail_url(tag_id):
    return reverse("recipe:tag-detail", args=(tag_id,))


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


def create_tag(user, name=TAG_DEFAULTS["name"]):
    recipe = Tag.objects.create(user=user, name=name)
    return recipe
