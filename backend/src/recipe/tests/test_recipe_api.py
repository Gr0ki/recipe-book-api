"""
Tests for the Recipe API.
"""
from decimal import Decimal

from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ..models import Recipe
from ..serializers import RecipeSerializer, RecipeDetailSerializer


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


class RecipeListTest(APITestCase, APIClient):
    """Tests GET the list of the recipes"""

    def setUp(self):
        """Creates client, user and two recipes records for the tests."""
        self.client = APIClient()

        self.user = create_user()
        self.client.force_authenticate(self.user)

        self.recipe = create_recipe(user=self.user)
        self.recipe = create_recipe(
            user=self.user,
            title="Test2 recipe name.",
            time_minutes=10,
            price=Decimal("300.33"),
            description="Test2 description.",
        )

    def test_list_recipes_success(self):
        """Test list recipes."""
        response = self.client.get(reverse("recipe:recipe-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        recipe_query = Recipe.objects.all().order_by("-id")
        self.assertEqual(len(response.data), recipe_query.count())

        serializer = RecipeSerializer(recipe_query, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_list_recipes_limited_access(self):
        """Test list recipes for a specific user."""
        user2 = create_user(email="test2@example.com")
        self.client.force_authenticate(user2)
        _ = create_recipe(user=user2)

        response = self.client.get(reverse("recipe:recipe-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        recipe_query = Recipe.objects.filter(user=user2).order_by("-id")
        self.assertEqual(len(response.data), recipe_query.count())

        serializer = RecipeSerializer(recipe_query, many=True)
        self.assertEqual(response.data, serializer.data)


class RecipeCreateTest(APITestCase, APIClient):
    """Tests POST a new recipe."""

    def setUp(self):
        """Creates user and client for the tests."""
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_create_recipe_success(self):
        """Test cration a new recipe."""
        payload = {
            "user": self.user,
            "title": "Test recipe name.",
            "time_minutes": 10,
            "price": Decimal("300.33"),
            "description": "Test description.",
        }
        response = self.client.post(reverse("recipe:recipe-list"), payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe_query = Recipe.objects.get(user=self.user.id, title=payload["title"])
        serializer = RecipeDetailSerializer(recipe_query)
        self.assertEqual(response.data, serializer.data)


class PrivateRecipeDetailedAPITest(APITestCase, APIClient):
    """Tests authorizations to call endpoint."""

    def setUp(self):
        """Creates client for the tests."""
        self.client = APIClient()
        self.user1 = create_user()
        self.user2 = create_user(email="test2@example.com")
        self.recipe1 = create_recipe(user=self.user1)
        self.recipe2 = create_recipe(user=self.user2)

    # ________________________________
    # Not authenticated:
    def test_get_auth_required(self):
        """Test auth is required to call the get method on the recipe-detailed endpoint."""
        response = self.client.get(create_recipe_detail_url(1), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_auth_required(self):
        """Test auth is required to call the put method on the recipe-detailed endpoint."""
        response = self.client.put(create_recipe_detail_url(1), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_auth_required(self):
        """Test auth is required to call the patch method on the recipe-detailed endpoint."""
        response = self.client.patch(create_recipe_detail_url(1), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_auth_required(self):
        """Test auth is required to call the delete method on the recipe-detailed endpoint."""
        response = self.client.delete(create_recipe_detail_url(1), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ________________________________
    # Authenticated but not authorized:

    def test_get_have_no_permissions(self):
        """Test restricted access for an unauthorized user
        to call the get method on the recipe-detailed endpoint."""
        self.client.login(**USER_DEFAULTS)
        response = self.client.get(create_recipe_detail_url(2), format="json")
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.login(email="test2@example.com", password=USER_DEFAULTS["password"])
        response = self.client.get(create_recipe_detail_url(1), format="json")
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_have_no_permissions(self):

        """Test restricted access for an unauthorized user
        to call the put method on the recipe-detailed endpoint."""
        self.client.login(**USER_DEFAULTS)
        response = self.client.put(create_recipe_detail_url(2), format="json")
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.login(email="test2@example.com", password=USER_DEFAULTS["password"])
        response = self.client.put(create_recipe_detail_url(1), format="json")
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_have_no_permissions(self):
        """Test restricted access for an unauthorized user
        to call the patch method on the recipe-detailed endpoint."""
        self.client.login(**USER_DEFAULTS)
        response = self.client.patch(create_recipe_detail_url(2), format="json")
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.login(email="test2@example.com", password=USER_DEFAULTS["password"])
        response = self.client.patch(create_recipe_detail_url(1), format="json")
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_have_no_permissions(self):
        """Test restricted access for an unauthorized user
        to call the delete method on the recipe-detailed endpoint."""
        self.client.login(**USER_DEFAULTS)
        response = self.client.delete(create_recipe_detail_url(2), format="json")
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.login(email="test2@example.com", password=USER_DEFAULTS["password"])
        response = self.client.delete(create_recipe_detail_url(1), format="json")
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RecipeDetailedTest(APITestCase, APIClient):
    """Tests retrive detailed recipe."""

    def setUp(self):
        """Creates client, user and recipe record for the tests."""
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    def test_retrive_recipe_detailed_success(self):
        """Test retrive recipe detailed."""
        response = self.client.get(create_recipe_detail_url(self.recipe.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        recipe_query = Recipe.objects.get(id=self.recipe.id)
        serializer = RecipeDetailSerializer(recipe_query)
        self.assertEqual(response.data, serializer.data)

    def test_retrive_recipe_detailed_does_not_exist(self):
        """Test retrive recipe detailed."""
        response = self.client.get(create_recipe_detail_url(22222))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UpdateDetailedTest(APITestCase, APIClient):
    """Tests update detailed recipe."""

    def setUp(self):
        """Creates client, user and recipe record for the tests."""
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    def test_put_recipe_detailed_success(self):
        """Test update(put) recipe detailed."""
        payload = RECIPE_DEFAULTS.copy()
        payload.update(user=self.user, time_minutes=10)
        response = self.client.put(create_recipe_detail_url(self.recipe.id), payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe_query = Recipe.objects.get(id=self.recipe.id)
        serializer = RecipeDetailSerializer(recipe_query)
        self.assertEqual(response.data, serializer.data)

    def test_put_recipe_detailed_error(self):
        """Test update(put) recipe detailed."""
        payload = RECIPE_DEFAULTS.copy()
        del payload["title"]
        response = self.client.put(create_recipe_detail_url(self.recipe.id), payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_recipe_detailed_success(self):
        """Test update(patch) recipe detailed."""
        payload = {"time_minutes": 20}
        response = self.client.patch(create_recipe_detail_url(self.recipe.id), payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        recipe_query = Recipe.objects.get(id=self.recipe.id)
        serializer = RecipeDetailSerializer(recipe_query)
        self.assertEqual(response.data, serializer.data)


class DeleteDetailedTest(APITestCase, APIClient):
    """Tests delete detailed recipe."""

    def setUp(self):
        """Creates client, user and recipe record for the tests."""
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    def test_delete_recipe_detailed_success(self):
        """Test delete recipe detailed."""
        response = self.client.delete(create_recipe_detail_url(self.recipe.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        recipe_query = Recipe.objects.count()
        self.assertEqual(recipe_query, 0)

    def test_delete_recipe_detailed_does_not_exist(self):
        """Test retrive recipe detailed."""
        response = self.client.delete(create_recipe_detail_url(2))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
