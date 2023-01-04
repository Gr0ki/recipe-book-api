from django.db.models import (
    Model,
    IntegerField,
    CharField,
    TextField,
    DecimalField,
    ForeignKey,
    ManyToManyField,
    SET_NULL,
    CASCADE,
)
from django.contrib.auth import get_user_model
from django.conf import settings


class Recipe(Model):
    user = ForeignKey(get_user_model(), null=True, on_delete=SET_NULL)
    title = CharField(max_length=40)
    time_minutes = IntegerField()
    price = DecimalField(decimal_places=2, max_digits=8)
    description = TextField()
    link = CharField(max_length=255, blank=True)
    tags = ManyToManyField("Tag", blank=True)

    def __str__(self):
        return f"user.id={self.user.id}, title={self.title}"


class Tag(Model):
    """Tag for filtering recipes."""

    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    name = CharField(max_length=255)

    def __str__(self):
        return f"user.id={self.user.id}, name={self.name}"
