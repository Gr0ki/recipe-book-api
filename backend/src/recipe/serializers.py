from rest_framework.serializers import ModelSerializer

from .models import Recipe, Tag


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fileds = ["id", "user", "name"]
        read_only_fields = ["id"]
        write_only_fields = ["user"]


class RecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ["id", "title", "time_minutes", "price", "link"]
        read_only_fields = ["id"]


class RecipeDetailSerializer(RecipeSerializer):
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description"]
