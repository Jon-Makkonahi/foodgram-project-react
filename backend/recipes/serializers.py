from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.serializers import CustomUserSerializer
from .models import (Favorite, Ingredient,
                     IngredientInRecipe, Purchase, Recipe, Tag)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class ShowRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Purchase.objects.filter(user=request.user, recipe=obj).exists()

    def get_ingredients(self, obj):
        objects = IngredientInRecipe.objects.filter(recipe=obj)
        serializer = IngredientRecipeSerializer(objects, many=True)
        return serializer.data


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = AddIngredientToRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(max_length=None, use_url=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time',
        )

    def validate(self, data):
        if len(data['tags']) == 0:
            raise serializers.ValidationError(
                'Необходимо добавить минимум 1 тег'
            )
        if len(data['tags']) > len(set(data['tags'])):
            raise serializers.ValidationError(
                'Теги не должны повторяться!'
            )
        if int(data['cooking_time']) <= 0:
            raise serializers.ValidationError(
                'Время готовки должно быть > 0 '
            )
        id_ingredients = []
        ingredients_set = data['ingredients']
        if len(ingredients_set) == 0:
            raise serializers.ValidationError('Заполните поле ingredients!')
        for ingredient in ingredients_set:
            id_ingredients.append(ingredient.get('id'))
        if len(id_ingredients) > len(set(id_ingredients)):
            raise serializers.ValidationError(
                'Ингредиенты повторяются!'
            )
        for ingredient in ingredients_set:
            try:
                Ingredient.objects.get(id=ingredient['id'])
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    'Такого ингредиента нет!'
                )
            amount = ingredient['amount']
            if amount == 0:
                raise serializers.ValidationError(
                    'amount не должно быть равно 0!'
                )
        return data

    def ingredient_create(self, ingredient_data, recipe):
        for ingredient in ingredient_data:
            ingredient_model = get_object_or_404(Ingredient, id=ingredient['id']) 
            amount = ingredient['amount']
            IngredientInRecipe.objects.create(
                ingredient=ingredient_model,
                recipe=recipe,
                amount=amount
            )
    
    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredient_data = validated_data.pop('ingredients')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(
            author=author, **validated_data)
        recipe.save()
        recipe.tags.set(tags_data)
        self.ingredient_create(ingredient_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredient_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        self.ingredient_create(ingredient_data, instance)
        instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        if validated_data.get('image') is not None:
            instance.image = validated_data.pop('image')
        instance.cooking_time = validated_data.pop('cooking_time')
        instance.save()
        instance.tags.set(tags_data)
        return instance

    def to_representation(self, instance):
        return ShowRecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data

class RecipeSerializer(RecipeCreateSerializer):
    tags = TagSerializer(many=True)
    image = serializers.ImageField(
        max_length=None,
        required=True,
        allow_empty_file=False,
        use_url=True,
    )


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id')
    recipe = serializers.IntegerField(source='recipe.id')

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']['id']
        recipe = data['recipe']['id']
        if Favorite.objects.filter(user=user, recipe__id=recipe).exists():
            raise serializers.ValidationError(
                'Нельзя добавить повторно в избранное!'
            )
        return data

    def create(self, validated_data):
        user = validated_data['user']
        recipe = validated_data['recipe']
        Favorite.objects.get_or_create(user=user, recipe=recipe)
        return validated_data


class PurchaseSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id')
    recipe = serializers.IntegerField(source='recipe.id')

    class Meta:
        model = Purchase
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']['id']
        recipe = data['recipe']['id']
        if Purchase.objects.filter(user=user, recipe__id=recipe).exists():
            raise serializers.ValidationError(
                'Нельзя добавить повторно в список!'
            )
        return data

    def create(self, validated_data):
        user = validated_data['user']
        recipe = validated_data['recipe']
        Purchase.objects.get_or_create(user=user, recipe=recipe)
        return validated_data
