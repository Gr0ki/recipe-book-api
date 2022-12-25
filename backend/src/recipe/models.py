from django.db.models import (
    Model,
    IntegerField,
    CharField,
    TextField,
    ForeignKey,
    DecimalField,
    SET_NULL,
)
from django.contrib.auth import get_user_model


class Recipe(Model):
    user = ForeignKey(get_user_model(), null=True, on_delete=SET_NULL)
    title = CharField(max_length=40)
    time_minutes = IntegerField()
    price = DecimalField(decimal_places=2, max_digits=8)
    description = TextField()
    link = CharField(max_length=255, blank=True)
