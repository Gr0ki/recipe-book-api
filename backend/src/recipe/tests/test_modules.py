"""
Tests for models.
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import Recipe


class ModelTests(TestCase):
    """Test models."""

    def setUp(self):
        """Creates user for all tests."""
        email = "test@example.com"
        password = "testpass123S"
        self.user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

    def test_create_recipe_successful(self):
        """Test creating a recipe successful."""
        recipe = Recipe.objects.create(
            user=self.user,
            title="Test recipe name.",
            time_minutes=5,
            price=Decimal("200.34"),
            description="Test description.",
        )
        recipes_query = Recipe.objects.all()
        self.assertIn(recipe, recipes_query)
        self.assertEqual(len(recipes_query), 1)
        self.assertEqual(recipes_query.get(user=self.user).user, self.user)
