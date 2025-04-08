from django.contrib.auth import get_user_model, login, logout
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, views, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from api import serializers
from community.models import Follow, Favorite, ShoppingCart
from api.filters import IngredientFilter, RecipeFilter
from api.paginators import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.utils import generate_short_url
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()


class UsersViewSet(
    viewsets.ModelViewSet
):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    pagination_class = CustomPagination

    @action(
        detail=False,
        methods=['get'],
        url_path='me',
        url_name='me',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def get_me(self, request):
        serializer = self.get_serializer_class()(
            request.user,
            context={'request': request}
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=[
            'put',
            'delete'
        ],
        url_path='me/avatar',
        url_name='avatar',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def avatar(self, request):
        user = get_object_or_404(
            User,
            username=request.user.username
        )
        if request.method == 'PUT':
            serializer = self.get_serializer_class()(
                user,
                data=request.data,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def get_serializer_class(self):
        serializers_by_actions = {
            'create': serializers.UserCreateSerializer,
            'avatar': serializers.AvatarSerializer,
            'set_password': serializers.PasswordSetSerializer
        }
        return serializers_by_actions.get(
            self.action,
            self.serializer_class
        )

    @action(
        detail=False,
        methods=['post'],
        url_path='set_password',
        url_name='set_password',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def set_password(self, request):
        user = self.request.user
        serializer = self.get_serializer_class()(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user.password = serializer.data.get('new_password')
        user.save()
        return Response(
            data='Пароль успешно изменен',
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        methods=['POST'],
        permission_classes=(permissions.IsAuthenticated,),
        detail=True,
    )
    def subscribe(self, request, pk=None):
        user = request.user
        following = get_object_or_404(User, pk=pk)

        serializer = serializers.FollowSerializer(
            data={'user': user.id, 'following': following.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        get_object_or_404(
            Follow,
            user=request.user,
            following=get_object_or_404(User, pk=pk)
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        permission_classes=(permissions.IsAuthenticated,),
        detail=False,
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)

        serializer = serializers.FollowGetSerializer(
            page,
            many=True,
            context={'request': request}
        )

        return self.get_paginated_response(serializer.data)


class TokenCreateView(views.APIView):
    serializer_class = serializers.TokenSerializer
    permission_classes = (permissions.AllowAny, )

    def post(self, request):
        serializer = serializers.TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            email=serializer.validated_data.get('email')
        )
        token, _ = Token.objects.get_or_create(
            user=user
        )
        login(request, user)
        message = {'auth_token': str(token.key)}
        return Response(
            message,
            status=status.HTTP_200_OK
        )


class TokenDeleteView(views.APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request):
        token_to_delete = get_object_or_404(
            Token,
            user=request.user
        )
        token_to_delete.delete()
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(
    viewsets.ModelViewSet
):
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

    @action(
        methods=['post', 'delete'],
        url_path='favorite',
        detail=True,
    )
    def add_to_favorite(self, request, pk):
        return self.add_recipe_to_favorites_or_cart(
            serializer=serializers.FavoriteSerializer,
            model=Favorite,
            pk=pk,
            request=request
        )

    @action(
        methods=['post', 'delete'],
        url_path='shopping_cart',
        detail=True,
        permission_classes=(permissions.IsAuthenticated, )
    )
    def add_to_shopping_cart(self, request, pk):
        return self.add_recipe_to_favorites_or_cart(
            serializer=serializers.ShoppingCartSerializer,
            model=ShoppingCart,
            pk=pk,
            request=request
        )

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
        shopping_list = self.prepare_recipes(shopping_cart_ingredients)
        return self.shop_list(shopping_list)

    def prepare_recipes(self, ingredients):
        shopping_list = []
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['total_amount']
            shopping_list.append(f'{name} {unit} - {amount}')
        shopping_list_text = '\n'.join(shopping_list)
        return shopping_list_text

    def shop_list(self, shop_list_text):
        response = HttpResponse(
            shop_list_text,
            content_type='text/plain',
        )
        response[
            'Content-Disposition'
        ] = 'attachment; file_name="shopping_list.txt'
        return response

    def add_recipe_to_favorites_or_cart(
            self,
            request,
            serializer,
            model,
            pk
    ):
        recipe = get_object_or_404(
            Recipe,
            id=pk
        )
        if request.method == 'POST':
            serializer = serializer(
                data={
                    'recipe': recipe.id,
                    'user': request.user.id,
                    'context': {'request': request}
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        recipe = model.objects.filter(
            user=request.user,
            recipe=recipe
        )
        if not recipe.exists():
            return Response(
                {'error': 'Рецепт не найден'},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class IngredientsViewSet(
    viewsets.ReadOnlyModelViewSet
):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientsSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class TagsViewSet(
    viewsets.ReadOnlyModelViewSet
):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    pagination_class = None


def recipe_by_short_link(request, short_link):
    recipe = get_object_or_404(
        Recipe,
        short_link=short_link
    )
    return redirect(
        'api:recipe-detail',
        pk=recipe.id
    )
