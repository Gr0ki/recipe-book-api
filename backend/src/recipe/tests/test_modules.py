"""
Tests for models.
"""

from django.test import TestCase

from ..models import Recipe
from .services import create_recipe, create_user


class RecipeModelTestCase(TestCase):
    """Test Recipe model."""

    def setUp(self):
        """Creates user for all tests."""
        self.user = create_user()

    def test_create_recipe_successful(self):
        """Test creating a recipe successful."""
        recipe = create_recipe(user=self.user)
        recipes_query = Recipe.objects.all()
        self.assertIn(recipe, recipes_query)
        self.assertEqual(len(recipes_query), 1)
        self.assertEqual(recipes_query.get(user=self.user).user, self.user)
