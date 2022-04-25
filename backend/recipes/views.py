from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from users.serializers import RecipeSubcribeSerializer
from users.pagination import LimitPageNumberPagination
from .filters import IngredientNameFilter, RecipeFilter
from .models import (Favorite, Ingredient, IngredientInRecipe,
                     Purchase, Recipe, Tag)
from .permissions import AdminOrAuthorOrReadOnly
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          FavoriteSerializer, PurchaseSerializer)

UNELECTED = 'Рецепта нет в избранном!'
NOT_ON_THE_LIST = 'В списке нет рецепта, который хотите удалить!'


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
            return RecipeSerializer
        return RecipeCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    @action(
        methods=['POST', 'DELETE'],
        url_path='favorite', url_name='favorite',
        permission_classes=[permissions.IsAuthenticated], detail=True
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = FavoriteSerializer(
            data={'user': request.user.id, 'recipe': recipe.id}
        )
        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save(recipe=recipe, user=request.user)
            serializer = RecipeSubcribeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            try:
                favorite = Favorite.objects.get(
                    user=request.user, recipe__id=pk
                )
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Favorite.DoesNotExist:
                return Response(
                    UNELECTED, status=status.HTTP_400_BAD_REQUEST
                )

    @action(
        methods=['POST', 'DELETE'],
        url_path='shopping_cart', url_name='shopping_cart',
        permission_classes=[permissions.IsAuthenticated], detail=True
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = PurchaseSerializer(
            data={'user': request.user.id, 'recipe': recipe.id}
        )
        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save(recipe=recipe, user=request.user)
            serializer = RecipeSubcribeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            try:
                favorite = Purchase.objects.get(
                    user=request.user, recipe__id=pk
                )
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Purchase.DoesNotExist:
                return Response(
                    NOT_ON_THE_LIST, status=status.HTTP_400_BAD_REQUEST
                )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_shopping_cart(request):
    user = request.user
    cart = user.purchase_set.all()
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
