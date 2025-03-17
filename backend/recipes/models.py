from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from foodgram_backend import constants
from users.models import User


class TagIngredientRecipeModel(models.Model):
    name = models.CharField(
        verbose_name='Name',
        max_length=100,
        unique=True,
        blank=False,
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:20]


class Tag(TagIngredientRecipeModel):
    slug = models.SlugField(
        verbose_name='Слаг тега',
        max_length=constants.TAG_MAX_LENGTH,
        unique=True,
        blank=True,
        null=True,
    )

    class Meta(TagIngredientRecipeModel.Meta):
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(TagIngredientRecipeModel):
    measurement_unit = models.CharField(
        max_length=constants.MEASUREMENT_UNIT_MAX_LENGTH,
        default='кг',
        verbose_name='Единица измерения'
    )

    class Meta(TagIngredientRecipeModel.Meta):
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(TagIngredientRecipeModel):
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=constants.RECIPE_NAME_MAX_LENGTH,
        unique=True,
        blank=False,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        blank=True,
        upload_to='recipes/',
        null=True,
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        blank=False,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        blank=False,
        db_index=True,
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
        verbose_name='Ингредиенты',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )

    class Meta(TagIngredientRecipeModel.Meta):
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'

    def get_absolute_url(self):
        return f'{settings.ALLOWED_HOSTS[0]}/recipes/{self.id}/'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=(
            MinValueValidator(constants.AMOUNT_MIN),
            MaxValueValidator(constants.AMOUNT_MAX),
        )
    )

    class Meta:
        default_related_name = 'recipe_ingredients'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient',
            ),
        )
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return f'Ингредиент {self.ingredient} в рецепте {self.recipe}'
