from django_filters.rest_framework import FilterSet, filters

from recipe.models import Ingredient, Recipe, Tag


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    """Кастомный фильтр. Позволяет фильтровать по нескольким значениям."""


class RecipeFilter(FilterSet):
    """Фильтр рецептов."""

    author = filters.NumberFilter(
        field_name='author__id'
    )

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        lookup_expr='in',
        to_field_name='slug'
    )

    is_favorited = filters.NumberFilter(
        method='filter_is_favorited'
    )

    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'author', 'tags', 'is_favorited', 'is_in_shopping_cart'
        )

    def filter_is_favorited(self, queryset, _, value):
        """Проверка наличия рецепта в избранном пользователя."""
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, _, value):
        """Проверка наличия рецепта в корзине покупок пользователя."""
        if value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class IngredientFilter(FilterSet):
    """Фильтр ингредиентов."""

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
