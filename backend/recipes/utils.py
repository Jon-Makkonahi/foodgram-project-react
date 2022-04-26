from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from users.serializers import RecipeSubcribeSerializer
from .models import Recipe


def obj_create(user, model, pk):
    recipe = get_object_or_404(Recipe, id=pk)
    if model.objects.filter(user=user, recipe=recipe).exists():
        return Response(
            'Повторный POST запрос!',
            status=status.HTTP_400_BAD_REQUEST
        )
    model.objects.create(user=user, recipe=recipe)
    serializer = RecipeSubcribeSerializer(recipe)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def obj_delete(user, model, pk):
    obj = model.objects.filter(user=user, recipe__id=pk).first()
    if obj is None:
        return Response(
            'Повторный DELETE запрос!',
            status=status.HTTP_400_BAD_REQUEST
        )
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
