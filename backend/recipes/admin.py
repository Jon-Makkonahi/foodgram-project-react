from django.contrib import admin

from .models import Favorites, Ingredient, IngredientInRecipe, Recipe, Tag


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user')


class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('id', 'name', 'measurement_unit',)
    search_fields = ('name',)


class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'ingredient', 'recipe', 'amount')


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name',)
    list_filter = ('author', 'name', 'tags')


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


admin.site.register(Favorites, FavoriteAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientInRecipe, IngredientInRecipeAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
