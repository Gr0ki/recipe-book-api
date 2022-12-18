"""
Tests for the User API.
"""
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class UserCreateTest(APITestCase, APIClient):
    """Tests different scenarios of user creation."""

    def setUp(self):
        """Create user for testing uniqueness of email field."""
        self.client = APIClient()
        self.url = reverse("user:create")

    def test_create_user_with_invalid_password(self):
        """Test user creations with invalid passwords."""
        data = (
            {"email": "test2@example.com", "name": "test2", "password": "t"},
            {
                "email": "test2@example.com",
                "name": "test2",
                "password": "test2@example.com",
            },
            {"email": "test2@example.com", "name": "test2", "password": "password"},
            {"email": "test2@example.com", "name": "test2", "password": "123456789"},
        )
        data = {
            "emails": (
                "test2@example.com",
                "test2@example.com",
                "test2@example.com",
                "test2@example.com",
            ),
            "passwords": ("t", "test2@example.com", "password", "123456789"),
        }
        for data in (data_frame for data_frame in data):
            response = self.client.post(self.url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_existed_email(self):
        """Test user creation with an email that is already taken."""
        data_for_existed_user = {
            "email": "existed@test.com",
            "name": "test",
            "password": "testPass13562",
        }
        get_user_model().objects.create_user(**data_for_existed_user)
        data = {"email": "existed@test.com", "name": "test3", "password": "testPass3"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_valid_credentials(self):
        """Test user creation with valid credentials."""
        data = {"email": "test4@example.com", "name": "test4", "password": "testPass4"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(get_user_model().objects.all().count(), 1)
        user = get_user_model().objects.get(email=data["email"])
        self.assertTrue(user.check_password(data["password"]))
        self.assertNotIn("password", response.data)
