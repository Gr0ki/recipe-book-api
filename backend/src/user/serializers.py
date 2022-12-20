"""Serializers for user app."""
from rest_framework.serializers import (
    Serializer,
    ModelSerializer,
    EmailField,
    CharField,
    ValidationError,
)
from rest_framework.exceptions import ValidationError as DRF_ValidationError

from django.core.exceptions import ValidationError as Django_ValidationError
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _
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

    def update(self, instance, validated_data):
        """Update and return user."""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(Serializer):
    """Serializer for generating authentication tokens."""

    email = EmailField()
    password = CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(
            request=self.context.get("request"), username=email, password=password
        )
        if not user:
            msg = _("Unable to authenticate with provided credentials.")
            raise ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs
