from django.db.models import Sum 
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
        recipe = IngredientInRecipe.objects.filter( 
            recipe__in_purchases__user=user 
        ) 
        ingredients = recipe.values( 
            'ingredient__name', 
            'ingredient__measurement_unit').annotate( 
            ingredients_total=Sum('amount') 
        ) 
        shopping_list = {} 
        for item in ingredients: 
            title = item.get('ingredient__name') 
            count = str(item.get('ingredient_total')) + ' ' + item[ 
                'ingredient__measurement_unit' 
            ] 
            shopping_list[title] = count 
        data = '' 
        for key, value in shopping_list.items(): 
            data += f'{key} - {value}\n' 
        return HttpResponse(data, content_type='text/plain')