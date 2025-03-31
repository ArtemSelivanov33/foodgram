import os

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from foodgram_backend import constants
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Name',
        max_length=constants.MODEL_NAME_LENGTH,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Слаг тега',
        max_length=constants.TAG_MAX_LENGTH,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Name',
        max_length=constants.MODEL_NAME_LENGTH,
    )
    measurement_unit = models.CharField(
        max_length=constants.MEASUREMENT_UNIT_MAX_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (models.UniqueConstraint(
            fields=['name', 'measurement_unit'],
            name='ingredients_uniques'
        ),)

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}.'


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=constants.RECIPE_NAME_MAX_LENGTH,
        unique=True,
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/',
    )
    text = models.TextField(
        'Описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=(
            MinValueValidator(constants.COOKING_TIME_MIN),
            MaxValueValidator(constants.COOKING_TIME_MAX),
        )
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        verbose_name='Ингредиент',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes'
    )
    created_at = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at',)

    def get_absolute_url(self):
        domain = os.getenv('DOMAIN', 'localhost')
        return f'{domain}/recipes/{self.pk}/'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='recipe_ingredients',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=(
            MinValueValidator(constants.AMOUNT_MIN),
            MaxValueValidator(constants.AMOUNT_MAX),
        )
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient',
            ),
        )


    def __str__(self):
        return f'Ингредиент {self.ingredient} в рецепте {self.recipe}'
