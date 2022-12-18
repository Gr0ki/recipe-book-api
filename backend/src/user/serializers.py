"""Serializers for user app."""
from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ValidationError as DRF_ValidationError

from django.core.exceptions import ValidationError as Django_ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password


class UserSerializer(ModelSerializer):
    """Serializer for the User object."""

    class Meta:
        model = get_user_model()
        fields = ["email", "password", "name"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, password):
        """Extends user data validation with password validation."""
        errors = dict()
        try:
            validate_password(password)
        except Django_ValidationError as err:
            errors["password"] = list(err.messages)
            raise DRF_ValidationError(errors)

        return super(UserSerializer, self).validate(password)

    def create(self, validated_data):
        """Validate password and create user with encripted password."""
        return get_user_model().objects.create_user(**validated_data)
