import django_filters
from django_filters.rest_framework import CharFilter, FilterSet

from recipes.models import Ingredient, Recipe


class IngredientFilter(FilterSet):
    name = CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
        ordering = ('name',)


class RecipeFilter(FilterSet):
    tags = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        lookup_expr='icontains',
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method='get_is_in_shopping_cart',
    )
    is_favorited = django_filters.NumberFilter(
        method='get_is_favorited',
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_in_shopping_cart', 'is_favorited')
        ordering = ('-created_at',)

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(
                cart_recipes__user=self.request.user
            )
        return queryset

    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(
                user_favorite__user=self.request.user
            )
        return queryset
