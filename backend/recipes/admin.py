from django.contrib import admin

from recipes.models import Ingredient, Recipe, Tag


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'image',
        'author',
        'text',
        'cooking_time',
        'favorites_count',
    )
    search_fields = ('name',)
    list_filter = (
        'author',
        'tags',
        'ingredients',
    )
    filter_horizontal = ('tags',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
    )
    list_editable = ('slug',)
    search_fields = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_editable = ('measurement_unit',)
    search_fields = ('name',)
