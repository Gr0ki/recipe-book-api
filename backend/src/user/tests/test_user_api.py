"""
Tests for the User API.
"""
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework.authtoken.models import Token


class UserCreateTest(APITestCase, APIClient):
    """Tests different scenarios of user creation."""

    def setUp(self):
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


class TestUserCreateToken(APITestCase, APIClient):
    """Tests different scenarios of creation a token for a user."""

    def setUp(self):
        """Set up class and create a user for the tests."""
        self.client = APIClient()
        self.url = reverse("user:token")
        self.user_details = {
            "email": "existed@test.com",
            "password": "testPass13562",
        }
        self.user_queryset = get_user_model().objects.create_user(**self.user_details)

    def test_crate_token_with_invalid_credentials(self):
        """Test token creation with invalid credentials."""
        invalid_credentials = self.user_details
        invalid_credentials["email"] = "????????@?????.???"
        invalid_credentials["password"] = "???????????"
        response = self.client.post(self.url, invalid_credentials, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", response.data)

    def test_crate_token_with_wrong_password(self):
        """Test token creation with wrong passwords."""
        invalid_credentials = self.user_details
        for password in ("", "sdf3", "sdffh2 834lK"):
            invalid_credentials["password"] = password
            response = self.client.post(self.url, invalid_credentials, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertNotIn("token", response.data)

    def test_create_token_with_valid_credentials(self):
        """Test token creation with valid credentials."""
        response = self.client.post(self.url, self.user_details, format="json")
        token = Token.objects.get(user=self.user_queryset)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["token"], token.key)
