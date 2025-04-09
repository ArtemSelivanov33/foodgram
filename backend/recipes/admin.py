from django.contrib import admin
from django import forms
from django.forms import BaseInlineFormSet

from recipes.models import Ingredient, Recipe, Tag, RecipeIngredient


class IngredientInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if not any(form.cleaned_data for form in self.forms):
            raise forms.ValidationError(
                'Необходимо добавить хотя бы один ингредиент.')


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    formset = IngredientInlineFormSet


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
    inlines = (IngredientInline,)
    search_fields = ('name',)
    list_filter = (
        'author',
        'tags',
    )
    filter_horizontal = ('tags',)

    @admin.display(description='Количество добавлений в избранное')
    def favorites_count(self, recipe):
        return recipe.user_favorite.count()


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
