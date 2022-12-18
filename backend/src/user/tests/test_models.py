"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = "test@example.com"
        password = "testpass123S"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ["  test1@example.com       ", "test1@example.com"],
            ["     TEST2@EXAMPLE.com   ", "TEST2@example.com"],
            ["test3@EXAMPLE.com", "test3@example.com"],
            ["Test4@Example.com", "Test4@example.com"],
            ["TEST5@EXAMPLE.com", "TEST5@example.com"],
            ["test6@example.COM", "test6@example.com"],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, "sample12S3eE")
            self.assertEqual(user.email, expected)

    def test_new_user_with_invalid_email(self):
        """Test email is invalid for a new user raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("testsdfIOD.com", "teDCst123A")

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "testO12Ld3")

    def test_create_superuser(self):
        """Test creating a superuser."""
        email = "testsuperuser@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password,
        )

        self.assertEqual(user.is_superuser, True)
        self.assertEqual(user.is_staff, True)
