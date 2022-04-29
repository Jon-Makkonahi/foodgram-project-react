from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from users.serializers import RecipeSubcribeSerializer

from .models import Recipe


def obj_create(user, model, pk, message):
    recipe = get_object_or_404(Recipe, id=pk)
    if model.objects.filter(user=user, recipe=recipe).exists():
        return Response(
            message,
            status=status.HTTP_400_BAD_REQUEST
        )
    model.objects.create(user=user, recipe=recipe)
    serializer = RecipeSubcribeSerializer(recipe)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def obj_delete(user, model, pk, message):
    obj = model.objects.filter(user=user, recipe__id=pk).first()
    if obj is None:
        return Response(
            message,
            status=status.HTTP_400_BAD_REQUEST
        )
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
