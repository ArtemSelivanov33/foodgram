from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from foodgram.backend.foodgram_backend.constants import (
    MODELS_FIELDS_MAX_LENGTH, TAG_COLOR_MAX_LENGTH, TAG_NAME_MAX_LENGTH
)


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        max_length=TAG_NAME_MAX_LENGTH,
        unique=True,
        verbose_name='Название тега'
    )
    color = models.CharField(
        max_length=TAG_COLOR_MAX_LENGTH,
        unique=True,
        verbose_name='Цвет тега',
        validators=[
            RegexValidator(
                regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Нарушен формат ввода цвета. #RGB или #RRGGBB.',
            )
        ]
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Слаг тега',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        max_length=MODELS_FIELDS_MAX_LENGTH,
        unique=True,
        verbose_name='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=MODELS_FIELDS_MAX_LENGTH,
        verbose_name='Название меры',
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient',
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    name = models.CharField(
        max_length=MODELS_FIELDS_MAX_LENGTH,
        unique=True,
        verbose_name='Название рецепта',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        through_fields=('recipe', 'ingredient'),
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='images/',
        help_text='Загрузка картинки к рецепту',
        blank=False
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[MinValueValidator(1, 'Не меньше 1 минуты.')]
    )
    pub_date = models.DateTimeField(
        'Дата публикации рецепта',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    """Модель связи рецепта и ингредиента."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1, 'Не меньше 1.')]
    )

    class Meta:
        verbose_name = 'Таблица рецепт-ингредиент.'
        verbose_name_plural = 'Таблица рецепт-ингредиент.'

    def __str__(self):
        return self.recipe.name


User = get_user_model()


class BaseUserRecipeRelation(models.Model):
    """Абстрактная модель для связи пользователя и рецепта."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(class)s'
    )

    class Meta:
        abstract = True


class Favorite(BaseUserRecipeRelation):
    """Модель избранных рецептов."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(BaseUserRecipeRelation):
    """Модель корзины."""

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Пользовательские корзины'

    def __str__(self):
        return self.user.username
