import base64
import uuid

from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, status
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.serializers import ImageField

from community.models import Favorite, Follow, ShoppingCart
from foodgram_backend import constants
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, image = data.split(';base64,')
            data = ContentFile(
                base64.b64decode(image), name=f'{uuid.uuid4()}.jpg'
            )
        return super().to_internal_value(data)


class UserCreateSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField(
        max_length=150,
        required=True,
    )
    last_name = serializers.CharField(
        max_length=150,
        required=True,
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
        )

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.save()
        return user

    def validate(self, attrs):
        excluded_attrs = {
            'first_name',
            'last_name',
            'password',
        }
        for name, value in attrs.items():
            if name in excluded_attrs:
                continue
            if User.objects.filter(**{name: value}).exists():
                raise serializers.ValidationError(
                    f'Пользователь с таким {name} уже существует.'
                )
        return attrs


class UserSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_followed'
    )
    avatar = Base64ImageField()

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
            'password': {'write_only': True}
        }

    def get_is_followed(self, following):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and request.user.follower.filter(
                following_id=following.id).exists()
        )


class TokenSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
    )
    password = serializers.CharField(
        required=True
    )

    def validate(self, attrs):
        user = get_object_or_404(
            User,
            email=attrs.get('email')
        )
        if user.password != attrs.get('password'):
            raise serializers.ValidationError(
                'Неверный пароль.'
            )
        return attrs


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = (
            'avatar',
        )


class PasswordSetSerializer(serializers.Serializer):
    new_password = serializers.CharField(
    )
    current_password = serializers.CharField(
    )

    def validate_new_password(self, new_password):
        try:
            validate_password(new_password)
        except serializers.ValidationError as error:
            raise serializers.ValidationError(error)
        return new_password

    def validate_current_password(self, current_password):
        user = self.context['request'].user
        if user.password != current_password:
            raise serializers.ValidationError(
                'Неверный пароль.'
            )
        return current_password


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
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
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
    )
    name = serializers.CharField(
        source='ingredient.name',
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = CreateRecipeIngredientSerializer(
        many=True,
        required=True,
        source='recipe_ingredients',
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True,
    )
    image = Base64ImageField()
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    cooking_time = serializers.IntegerField(
        min_value=constants.COOKING_TIME_MIN,
        max_value=constants.COOKING_TIME_MAX,
        required=True
    )

    class Meta:
        model = Recipe
        fields = '__all__'

    def create(self, value):
        recipe, _ = self.add_update_recipe_ingredients(value)
        return recipe

    def update(self, recipe, value):
        recipe, value = self.add_update_recipe_ingredients(
            value,
            recipe
        )
        return super().update(recipe, value)

    def to_representation(self, instance):
        return RecipeDetailSerializer(
            instance,
            context={
                'request': self.context.get('request'),
            }
        ).data

    def validate(self, attrs):
        tags = attrs.get('tags')
        ingredients = attrs.get('recipe_ingredients')
        for field in (tags, ingredients):
            if not field:
                raise serializers.ValidationError(
                    f'Отсутсвует обязательное поле {field}'
                )
        ingredients_id = [
            ingredient['ingredient'].id for ingredient in ingredients
        ]
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'Теги не могут повторяться'
            )
        if len(ingredients_id) != len(set(ingredients_id)):
            raise serializers.ValidationError(
                'Ингредиенты не могут повторяться'
            )
        return attrs

    def add_update_recipe_ingredients(self, value, recipe=None):
        ingredients = value.pop('recipe_ingredients')
        tags = value.pop('tags')
        if not recipe:
            recipe = Recipe.objects.create(**value)
        recipe.recipe_ingredients.all().delete()
        recipe.tags.clear()
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                **ingredient
            ) for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(
            recipe_ingredients
        )
        recipe.tags.set(tags)
        return recipe, value


class RecipeDetailSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeSerializer(
        read_only=True,
        many=True,
        source='recipe_ingredients'
    )
    tags = TagSerializer(
        read_only=True,
        many=True,
    )
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, obj):
        request = self.context['request']
        user = request.user
        return (request and request.user.is_authenticated
                and user.user_favorite.filter(
                    recipe=obj
                ).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        user = request.user
        return (request and request.user.is_authenticated
                and user.cart_recipes.filter(
                    recipe=obj
                ).exists())


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = (
            'user',
            'following'
        )

    def validate(self, attrs):
        user = attrs.get('user')
        following = attrs.get('following')

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


class FollowGetSerializer(
    UserSerializer
):
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes'
    )
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

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

    def get_is_subscribed(self, user):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and request.user.follower.filter(folowing_id=user.id).exists()
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context['request']
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = instance.recipes.all()
        if recipes_limit and recipes_limit.isdigit():
            recipes = recipes[:int(recipes_limit)]
        representation['recipes'] = RecipeShortSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data
        representation['recipes_count'] = recipes.count()
        return representation


class RecipeShortSerializer(serializers.ModelSerializer):

    image = Base64ImageField()

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
