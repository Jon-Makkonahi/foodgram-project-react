from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.serializers import CustomUserSerializer

from .models import (Favorites, Ingredient,
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


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
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

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorites.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Purchase.objects.filter(user=request.user, recipe=obj).exists()

    def get_ingredients(self, obj):
        objects = IngredientInRecipe.objects.filter(recipe=obj)
        serializer = IngredientRecipeSerializer(objects, many=True)
        return serializer.data

    def validate(self, data):
        request = self.context.get('request')
        if len(data['tags']) == 0:
            raise serializers.ValidationError(
                'Необходимо добавить минимум 1 тег'
            )
        if len(data['tags']) > len(set(data['tags'])):
            raise serializers.ValidationError(
                'Теги не должны повторяться!')
        id_ingredients = []
        try:
            ingredients_set = request.data['ingredients']
        except KeyError:
            raise serializers.ValidationError(
                'Необходимо добавить ингридиенты к рецепту!'
            )
        if ingredients_set == []:
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

    def create(self, validated_data):
        request = self.context.get('request')
        tags = validated_data.pop('tags')
        ingredients_set = request.data['ingredients']
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients_set:
            ingredient_model = Ingredient.objects.get(id=ingredient['id'])
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient_model,
                amount=ingredient['amount']
            )
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        recipe = instance
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
            )
        instance.save()
        instance.tags.set(tags)
        IngredientInRecipe.objects.filter(recipe=recipe).delete()
        ingredients = self.initial_data.get('ingredients')
        for ingredient in ingredients:
            ingredient_model = Ingredient.objects.get(id=ingredient.get('id'))
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient_model,
                amount=ingredient.get('amount')
                )
        return instance


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
        model = Favorites
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']['id']
        recipe = data['recipe']['id']
        if Favorites.objects.filter(user=user, recipe__id=recipe).exists():
            raise serializers.ValidationError(
                'Нельзя добавить повторно в избранное!'
            )
        return data

    def create(self, validated_data):
        user = validated_data['user']
        recipe = validated_data['recipe']
        Favorites.objects.get_or_create(user=user, recipe=recipe)
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
