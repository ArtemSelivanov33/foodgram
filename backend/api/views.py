import csv
# from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from djoser import views
from rest_framework.views import APIView
from rest_framework import permissions, status, viewsets
# from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

# from api import views_utils
# from api.pagination import LimitedPagination
from api.permissions import ThisUserOrAdmin
from api.serializers import (
    CustomUserSerializer,
    IngredientDetailSerializer,
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    # SpecialRecipeSerializer,
    # RecipeCreateSerializer,
    # RecipeListSerializer,
    RecipeSerializer,
    # RecipeSerializerShort,
    SubscriptionListSerializer,
    TagSerializer
)
from recipe.models import (
    Ingredient, Recipe, Tag
)
from user.models import User, Follow
from utils.text_constants import Message
from api.filters import (
    IngredientFilter, TagFilter
)


class UserListViewSet(views.UserViewSet):
    """Представление пользователей."""

    queryset = User.objects.all()
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        ThisUserOrAdmin
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('username', 'email')

    def get_queryset(self):
        queryset = super().get_queryset()
        limit = self.request.query_params.get('limit')
        if limit:
            queryset = queryset[:int(limit)]
        return queryset

    @action(
        detail=False,
        url_path='subscriptions',
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        """Получение подписок и сериализация."""
        authors = User.objects.filter(following__user=request.user)
        paginator = PageNumberPagination()
        paginator.page_size = 6
        result_page = paginator.paginate_queryset(authors, request)
        serializer = SubscriptionListSerializer(
            result_page,
            many=True,
            context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='subscribe',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id):
        """Подписка на автора, отписка."""
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if user != author and not Follow.objects.filter(
                user=user,
                author=author
            ).exists():
                Follow.objects.create(user=request.user, author=author)
                follows = User.objects.filter(id=id).first()
                serializer = SubscriptionListSerializer(
                    follows,
                    context={'request': request}
                )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'errors': Message.ErrorMessage.SUBSCRIPTION_ERROR},
                status=status.HTTP_400_BAD_REQUEST
            )
        if user != author and Follow.objects.filter(
            user=user,
            author=author
        ).exists():
            Follow.objects.filter(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': Message.ErrorMessage.NO_ENTRY},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        url_path='me',
        methods=('get', 'patch'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        """Представление авторизованного пользователя."""
        if request.method == 'GET':
            serializer = CustomUserSerializer(
                request.user,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagViewset(viewsets.ReadOnlyModelViewSet):
    """Представление тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    filterset_class = TagFilter


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientDetailSerializer
    search_fields = ('name',)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        is_favorited = self.request.query_params.get('is_favorited')
        author_id = self.request.query_params.get('author')
        tags = self.request.query_params.getlist('tags')

        if is_favorited is not None:
            queryset = queryset.filter(is_favorited=self.request.user)
        if author_id is not None:
            queryset = queryset.filter(author__id=author_id)
        if tags:
            queryset = queryset.filter(tags__slug__in=tags)

        return queryset

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            recipe.is_favorited.add(user)
            return Response(
                {'status': 'added to favorites'},
                status=status.HTTP_201_CREATED
            )
        elif request.method == 'DELETE':
            recipe.is_favorited.remove(user)
            return Response(
                {'status': 'removed from favorites'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            recipe.shopping_cart.add(user)
            return Response(
                {'status': 'added to shopping cart'},
                status=status.HTTP_201_CREATED
            )
        elif request.method == 'DELETE':
            recipe.shopping_cart.remove(user)
            return Response(
                {'status': 'removed from shopping cart'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False, methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        recipes = user.shopping_cart_recipes.all()

        response = HttpResponse(content_type='text/csv')
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopping_cart.csv"'

        writer = csv.writer(response)
        writer.writerow(['Ingredient', 'Amount', 'Measurement Unit'])

        ingredients = {}
        for recipe in recipes:
            for item in recipe.ingredientsinrecipe_set.all():
                ingredient_name = item.ingredient.name
                if ingredient_name in ingredients:
                    ingredients[ingredient_name]['amount'] += item.amount
                else:
                    ingredients[ingredient_name] = {
                        'amount': item.amount,
                        'measurement_unit': item.ingredient.measurement_unit,
                    }

        for ingredient, data in ingredients.items():
            writer.writerow(
                [ingredient, data['amount'],
                 data['measurement_unit']]
            )

        return response


class CustomUserViewSet(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Регистрация пользователя
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": "Пользователь успешно зарегистрирован."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post_token(self, request):
        # Получение токена
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    def delete_token(self, request):
        # Удаление токена
        try:
            # Удаление токена
            token = request.META['HTTP_AUTHORIZATION'].split(' ')[1]
            token_obj = RefreshToken(token)
            token_obj.blacklist()  # Блокируем токен
            return Response(
                {"success": "Токен успешно удален."},
                status=status.HTTP_205_RESET_CONTENT
            )
        except (AttributeError, ValueError):
            return Response(
                {"": "Токен не предоставлен."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except TokenError:
            return Response(
                {"": "Неверный токен."},
                status=status.HTTP_401_UNAUTHORIZED
            )
