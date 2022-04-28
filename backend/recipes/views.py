from django.http.response import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from rest_framework.decorators import action

from users.pagination import LimitPageNumberPagination
from .filters import IngredientNameFilter, RecipeFilter
from .models import (Favorite, Ingredient, IngredientInRecipe,
                     Purchase, Recipe, Tag)
from .permissions import AdminOrAuthorOrReadOnly
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeCreateSerializer, ShowRecipeSerializer)
from .utils import obj_create, obj_delete

UNELECTED = 'Рецепта нет в избранном!'
ERROR_FAVORITE = 'Рецепт уже есть в избранном!'
NOT_ON_THE_LIST = 'В списке нет рецепта, который хотите удалить!'
ERROR_ON_THE_LIST = 'Рецепт уже есть в списке!'


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filterset_class = IngredientNameFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (AdminOrAuthorOrReadOnly,)
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ShowRecipeSerializer
        return RecipeCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    @action(
        methods=['POST', 'DELETE'],
        permission_classes=[permissions.IsAuthenticated], detail=True
    )
    def favorite(self, request, pk):
        user = request.user
        model = Favorite
        if request.method == 'POST':
            return obj_create(user, model, pk=pk, message=ERROR_FAVORITE)
        if request.method == 'DELETE':
            return obj_delete(user, model, pk=pk, message=UNELECTED)

    @action(
        methods=['POST', 'DELETE'],
        permission_classes=[permissions.IsAuthenticated], detail=True
    )
    def shopping_cart(self, request, pk):
        user = request.user
        model = Purchase
        if request.method == 'POST':
            return obj_create(user, model, pk=pk, message=ERROR_ON_THE_LIST)
        if request.method == 'DELETE':
            return obj_delete(user, model, pk=pk, message=NOT_ON_THE_LIST)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        cart = user.purchase_recipes.all()
        buying_list = {}
        for item in cart:
            recipe = item.recipe
            ingredients_in_recipe = IngredientInRecipe.objects.filter(
                recipe=recipe
            )
            for item in ingredients_in_recipe:
                amount = item.amount
                name = item.ingredient.name
                measurement_unit = item.ingredient.measurement_unit
                if name not in buying_list:
                    buying_list[name] = {
                        'amount': amount,
                        'measurement_unit': measurement_unit
                    }
                else:
                    buying_list[name]['amount'] = (
                        buying_list[name]['amount'] + amount
                    )
        shopping_list = []
        for item in buying_list:
            shopping_list.append(
                f'{item} - {buying_list[item]["amount"]}, '
                f'{buying_list[item]["measurement_unit"]}\n'
            )
        response = HttpResponse(shopping_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = (
            'attachment;' 'filename="shopping_list.txt"'
        )
        return response
