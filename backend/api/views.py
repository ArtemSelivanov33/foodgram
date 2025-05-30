import os

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as BaseUserViewSet
from hashlib import blake2b
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from api import serializers
from api.filters import IngredientFilter, RecipeFilter
from api.paginators import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from community.models import Follow, Favorite, ShoppingCart, ShortLink
from foodgram_backend.constants import DIGEST_SIZE
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()


class UsersViewSet(BaseUserViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)

    def get_permissions(self):
        if self.action == 'me':
            return (permissions.IsAuthenticated(),)
        return super().get_permissions()

    @action(
        detail=False,
        methods=['PUT'],
        url_path='me/avatar',
        url_name='avatar',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def avatar(self, request):
        serializer = serializers.AvatarSerializer(
            self.get_instance(),
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @avatar.mapping.delete
    def delete_avatar(self, request):
        request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST'],
        permission_classes=(permissions.IsAuthenticated,),
        detail=True,
    )
    def subscribe(self, request, id=None):
        following = get_object_or_404(User, pk=id)
        serializer = serializers.FollowSerializer(
            data={
                'user': request.user.id, 'author': following.id
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        get_object_or_404(
            Follow,
            user=request.user,
            following=get_object_or_404(User, pk=id)
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        url_path='subscriptions',
        permission_classes=(permissions.IsAuthenticated,),
        detail=False,
    )
    # я не понял до конца,мне надо именно метод list() прописать?
    # так его не получается в @action завернуть, как по другому, я не знаю.
    # у меня уже не остается времени, в среду последний день сдачи проекта.
    def subscriptions(self, request):
        queryset = self.filter_queryset(
            User.objects.filter(following__user=request.user)
        )
        pages = self.paginate_queryset(queryset)
        if pages is not None:
            serializer = serializers.FollowGetSerializer(
                pages, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly
    )
    serializer_class = serializers.RecipeCreateSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.RecipeDetailSerializer
        return serializers.RecipeCreateSerializer

    def generate_short_url(self, url):
        domain = os.getenv('DOMAIN', 'localhost')
        base_url = f'https://{domain}/'
        hash_url = blake2b(url.encode(), digest_size=DIGEST_SIZE).hexdigest()
        return f'{base_url}{hash_url}'

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
        url_name='get_link',
    )
    def get_short_link(self, request, pk):
        domain = os.getenv('DOMAIN', 'localhost')
        recipe = get_object_or_404(Recipe, id=pk)
        recipe_url = f'https://{domain}/recipes/{recipe.pk}/'
        short_link = self.generate_short_url(recipe_url)
        short_link_obj, created = ShortLink.objects.get_or_create(
            full_url=recipe_url,
            defaults={'short_link': short_link, 'recipe': recipe}
        )
        return Response(
            {'short-link': str(short_link_obj.full_url)},
            status=status.HTTP_200_OK
        )

    @action(
        methods=['POST'],
        url_path='favorite',
        detail=True,
    )
    def add_to_favorite(self, request, pk=None):
        return self._add_recipe(
            serializer_class=serializers.FavoriteSerializer,
            pk=pk
        )

    @action(
        methods=['POST'],
        url_path='shopping_cart',
        detail=True,
        permission_classes=(permissions.IsAuthenticated, )
    )
    def add_to_shopping_cart(self, request, pk=None):
        return self._add_recipe(
            serializer_class=serializers.ShoppingCartSerializer,
            pk=pk
        )

    @add_to_favorite.mapping.delete
    def remove_from_favorite(self, request, pk=None):
        return self._remove_recipe(Favorite, pk)

    @add_to_shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk=None):
        return self._remove_recipe(ShoppingCart, pk)

    @action(
        methods=['get'],
        url_path='download_shopping_cart',
        detail=False,
        permission_classes=(permissions.IsAuthenticated, )
    )
    def download_shopping_cart(self, request):
        shopping_cart_ingredients = (
            RecipeIngredient.objects.filter(
                recipe__cart_recipes__user=request.user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit'
            ).annotate(total_amount=Sum('amount')).order_by('ingredient__name')
        )
        shopping_list = self._prepare_recipes(shopping_cart_ingredients)
        return self.forming_shopping_list(shopping_list)

    def _prepare_recipes(self, ingredients):
        shopping_list = []
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['total_amount']
            shopping_list.append(f'{name} {unit} - {amount}')
        shopping_list_text = '\n'.join(shopping_list)
        return shopping_list_text

    def forming_shopping_list(self, shop_list_text):
        response = HttpResponse(
            shop_list_text,
            content_type='text/plain',
        )
        response[
            'Content-Disposition'
        ] = 'attachment; file_name="shopping_list.txt'
        return response

    def _add_recipe(self, serializer_class, pk):
        serializer = serializer_class(
            data={
                'recipe': get_object_or_404(Recipe, id=pk).id,
                'user': self.request.user.id,
                'context': {'request': self.request}
            }
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def _remove_recipe(self, model, pk):
        get_object_or_404(
            model,
            user=self.request.user,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientsSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    pagination_class = None
