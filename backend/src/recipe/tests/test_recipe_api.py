"""
Tests for the Recipe API.
"""
from decimal import Decimal

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .services import (
    RECIPE_LIST_URL,
    RECIPE_DEFAULTS,
    create_recipe_detail_url,
    create_user,
    create_recipe,
)
from ..models import Recipe, Tag
from ..serializers import RecipeSerializer, RecipeDetailSerializer


# ________
# GET,POST /api/recipes/:


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
        response = self.client.get(RECIPE_LIST_URL)
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

        response = self.client.get(RECIPE_LIST_URL)
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
        payload = RECIPE_DEFAULTS.copy()
        response = self.client.post(RECIPE_LIST_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe_query = Recipe.objects.get(user=self.user.id, title=payload["title"])
        serializer = RecipeDetailSerializer(recipe_query)
        self.assertEqual(response.data, serializer.data)

    def test_create_recipe_with_new_tags_success(self):
        """Test creating a recipe with new tags."""
        payload = RECIPE_DEFAULTS.copy()
        payload["tags"] = [{"name": "tag1"}, {"name": "tag2"}]
        response = self.client.post(RECIPE_LIST_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipes_query = Recipe.objects.filter(user=self.user.id)
        self.assertEqual(recipes_query.count(), 1)
        recipes_query = recipes_query[0]
        self.assertEqual(recipes_query.tags.count(), 2)
        for tag in payload["tags"]:
            exists = recipes_query.tags.filter(
                name=tag["name"], user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tag."""
        tag = Tag.objects.create(user=self.user, name="tag-name1")
        payload = RECIPE_DEFAULTS.copy()
        payload["tags"] = [{"name": "tag-name1"}, {"name": "tag-name2"}]
        response = self.client.post(RECIPE_LIST_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipes_query = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes_query.count(), 1)
        recipe = recipes_query[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag, recipe.tags.all())
        for tag in payload["tags"]:
            exists = recipe.tags.filter(
                name=tag["name"],
                user=self.user,
            ).exists()
            self.assertTrue(exists)


class RecipeListNotAuthenticatedAPITest(APITestCase, APIClient):
    """Tests calling endpoint with the unauthenticated user."""

    def setUp(self):
        """Creates client for the tests."""
        self.client = APIClient()

    def test_get_auth_required(self):
        """Test auth is required to call the get method on the recipe-list endpoint."""
        response = self.client.get(RECIPE_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_recipe_success(self):
        """Test cration a new recipe without authentication."""
        payload = RECIPE_DEFAULTS.copy()
        response = self.client.post(RECIPE_LIST_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ________
# GET,PUT,PATCH,DELETE /api/recipes/{id}/:


class RecipeDetailedNotAuthenticatedAPITest(APITestCase, APIClient):
    """Tests calling endpoint with the unauthenticated user."""

    def setUp(self):
        """Creates client and recipe for the tests."""
        self.client = APIClient()
        self.user = create_user()
        self.recipe = create_recipe(user=self.user)

    def test_get_auth_required(self):
        """
        Test auth is required to call the get method
        on the recipe-detailed endpoint.
        """
        response = self.client.get(
            create_recipe_detail_url(self.recipe.id), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_auth_required(self):
        """
        Test auth is required to call the put method
        on the recipe-detailed endpoint.
        """
        response = self.client.put(
            create_recipe_detail_url(self.recipe.id), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_auth_required(self):
        """
        Test auth is required to call the patch method
        on the recipe-detailed endpoint.
        """
        response = self.client.patch(
            create_recipe_detail_url(self.recipe.id), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_auth_required(self):
        """
        Test auth is required to call the delete method
        on the recipe-detailed endpoint.
        """
        response = self.client.delete(
            create_recipe_detail_url(self.recipe.id), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RecipeDetailedNotAuthorizedAPITest(APITestCase, APIClient):
    """Tests authorizations for authenticated user to call endpoint."""

    def setUp(self):
        """Creates client for the tests."""
        self.client = APIClient()
        self.user1 = create_user()
        self.user2 = create_user(email="test2@example.com")
        self.recipe1 = create_recipe(user=self.user1)
        self.recipe2 = create_recipe(user=self.user2)

    def test_get_have_no_permissions(self):
        """Test restricted access for an unauthorized user
        to call the get method on the recipe-detailed endpoint."""
        self.client.force_authenticate(self.user1)
        response = self.client.get(
            create_recipe_detail_url(self.recipe2.id), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_authenticate(self.user2)
        response = self.client.get(
            create_recipe_detail_url(self.recipe1.id), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_have_no_permissions(self):

        """Test restricted access for an unauthorized user
        to call the put method on the recipe-detailed endpoint."""
        self.client.force_authenticate(self.user1)
        response = self.client.put(
            create_recipe_detail_url(self.recipe2.id), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_authenticate(self.user2)
        response = self.client.put(
            create_recipe_detail_url(self.recipe1.id), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_have_no_permissions(self):
        """Test restricted access for an unauthorized user
        to call the patch method on the recipe-detailed endpoint."""
        self.client.force_authenticate(self.user1)
        response = self.client.patch(
            create_recipe_detail_url(self.recipe2.id), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_authenticate(self.user2)
        response = self.client.patch(
            create_recipe_detail_url(self.recipe1.id), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_have_no_permissions(self):
        """Test restricted access for an unauthorized user
        to call the delete method on the recipe-detailed endpoint."""
        self.client.force_authenticate(self.user1)
        response = self.client.delete(
            create_recipe_detail_url(self.recipe2.id), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_authenticate(self.user2)
        response = self.client.delete(
            create_recipe_detail_url(self.recipe1.id), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


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
        self.recipe.refresh_from_db()
        for key, value in payload.items():
            self.assertEqual(getattr(self.recipe, key), value)

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

        self.recipe.refresh_from_db()
        for key, value in payload.items():
            self.assertEqual(getattr(self.recipe, key), value)

    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe."""
        tag1 = Tag.objects.create(user=self.user, name="tag-name")
        self.recipe.tags.add(tag1)

        tag2 = Tag.objects.create(user=self.user, name="tag-name1")
        payload = {"tags": [{"name": tag2.name}]}
        response = self.client.patch(
            create_recipe_detail_url(self.recipe.id), payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(tag2, self.recipe.tags.all())
        self.assertNotIn(tag1, self.recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing a recipes tags."""
        tag = Tag.objects.create(user=self.user, name="tag-name2")
        self.recipe.tags.add(tag)
        payload = {"tags": []}
        response = self.client.patch(
            create_recipe_detail_url(self.recipe.id), payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.recipe.tags.count(), 0)


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
        self.assertFalse(Recipe.objects.filter(id=self.recipe.id).exists())

    def test_delete_recipe_detailed_does_not_exist(self):
        """Test retrive recipe detailed."""
        user2 = create_user(email="test2@test.com")
        recipe = create_recipe(user=user2)
        response = self.client.delete(create_recipe_detail_url(recipe.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())
