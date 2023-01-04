"""
Tests for models.
"""

from django.test import TestCase

from ..models import Tag
from .services import create_recipe, create_user


class RecipeModelTestCase(TestCase):
    """Test Recipe model."""

    def setUp(self):
        """Creates user for all tests."""
        self.user = create_user()

    def test_create_recipe_successful(self):
        """Test creating a recipe successful."""
        recipe_title = "Test title"
        recipe = create_recipe(user=self.user, title=recipe_title)
        self.assertEqual(recipe.user, self.user)
        self.assertEqual(str(recipe), f"user.id={self.user.id}, title={recipe_title}")


class TagModelTestCase(TestCase):
    """Test Tag model."""

    def setUp(self):
        self.user = create_user()

    def test_create_tag_successfuly(self):
        """Test creating a tag successful."""
        tag_name = "Test tag name"
        tag = Tag.objects.create(name=tag_name, user=self.user)
        self.assertEqual(tag_name, tag.name)
        self.assertEqual(self.user, tag.user)
        self.assertEqual(str(tag), f"user.id={self.user.id}, name={tag_name}")
