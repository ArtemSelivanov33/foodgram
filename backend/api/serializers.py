from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.validators import UniqueTogetherValidator

from community.models import Favorite, Follow, ShoppingCart
from foodgram_backend import constants
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )
        extra_kwargs = {
            'password': {
                'write_only': True,
            }
        }

    def get_is_subscribed(self, following):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and request.user.follower.filter(
                following_id=following.id).exists()
        )


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    amount = serializers.IntegerField(
        min_value=constants.AMOUNT_MIN,
        max_value=constants.AMOUNT_MAX,
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
        )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )
    name = serializers.ReadOnlyField(source='ingredient.name')

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = CreateRecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=constants.COOKING_TIME_MIN,
        max_value=constants.COOKING_TIME_MAX,
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def create(self, value):
        ingredients = value.pop('ingredients')
        tags = value.pop('tags')

        value['author'] = self.context.get('request').user
        recipe = Recipe.objects.create(**value)
        self._add_recipe_ingredients(recipe, ingredients)
        recipe.tags.set(tags)

        return recipe

    def update(self, recipe, value):
        ingredients = value.pop('ingredients')
        tags = value.pop('tags')

        recipe.tags.clear()
        recipe.tags.set(tags)
        recipe.ingredients.clear()
        self._add_recipe_ingredients(recipe, ingredients)

        return super().update(recipe, value)

    def to_representation(self, instance):
        return RecipeDetailSerializer(
            instance,
            context={
                'request': self.context.get('request'),
            }
        ).data

    # def validate(self, attrs):
    #     tags = attrs.get('tags')
    #     ingredients = attrs.get('ingredients')
    #     for field in (tags, ingredients):
    #         if not field:
    #             raise serializers.ValidationError(
    #                 f'Отсутсвует обязательное поле {field}'
    #             )
    #     ingredients_id = [
    #         ingredient['id'].id for ingredient in ingredients
    #     ]
    #     if len(tags) != len(set(tags)):
    #         raise serializers.ValidationError(
    #             'Теги не могут повторяться'
    #         )
    #     if len(ingredients_id) != len(set(ingredients_id)):
    #         raise serializers.ValidationError(
    #             'Ингредиенты не могут повторяться'
    #         )
    #     return attrs

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                "Отсутствует обязательное поле 'tags'"
            )

        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "Теги не могут повторяться"
            )

        return value

    def _add_recipe_ingredients(self, instance, ingredients):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=instance,
                ingredient=item.get('id'),
                amount=item.get('amount'),
            )
            for item in ingredients
        )


class RecipeDetailSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='recipe_ingredients',
        allow_empty=False,
    )
    tags = TagSerializer(
        read_only=True,
        many=True,
    )
    author = UserSerializer(read_only=True, many=False)
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        request = self.context['request']
        user = request.user
        return (
            request and request.user.is_authenticated
            and user.user_favorite.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        user = request.user
        return (
            request and request.user.is_authenticated
            and user.cart_recipes.filter(recipe=obj).exists()
        )


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class FollowSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='following'
    )

    class Meta:
        model = Follow
        fields = (
            'user',
            'author'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author'),
                message='Подписка уже существует'
            )
        ]

    def validate(self, attrs):
        user = attrs.get('user')
        following = attrs.get('author')

        if user == following:
            raise serializers.ValidationError(
                detail='Нельзя подписаться на самого себя.',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user.following.filter(following=following).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя.',
                code=status.HTTP_400_BAD_REQUEST
            )

        return attrs

    def to_representation(self, instance):
        request = self.context.get('request')
        return FollowGetSerializer(
            instance.following,
            context={'request': request}
        ).data


class FollowGetSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes'
    )
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
        )

    def get_recipes(self, author):
        recipes = author.recipes.all()
        request = self.context.get('request')

        if 'recipes_limit' in self.context['request'].GET:
            recipes_limit = self.context['request'].GET['recipes_limit']
            if recipes_limit.isdigit():
                recipes = recipes[:int(recipes_limit)]
        return RecipeShortSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, user):
        return user.recipes.count()


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
            )
        ]

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
        ).data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
            )
        ]

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
        ).data
