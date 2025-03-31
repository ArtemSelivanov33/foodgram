from django.db import models

from recipes.models import Recipe
from users.models import User


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique_follow',
            ),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_prevent_self_follow',
                check=~models.Q(user=models.F('following')),
            )
        )

    def __str__(self):
        return f'{self.user} подписан на {self.following}'


class FavoriteShoppingCartMixin(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Избранные рецепты',
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_unique',
            ),
        )


class Favorite(FavoriteShoppingCartMixin):

    class Meta(FavoriteShoppingCartMixin.Meta):
        default_related_name = 'user_favorite'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'


class ShortLink(models.Model):
    full_url = models.URLField(
        verbose_name='Полная ссылка',
        unique=True,
    )
    short_link = models.URLField(
        unique=True,
    )
    recipe = models.OneToOneField(
        Recipe,
        on_delete=models.CASCADE,
        related_name='short_link',
    )

    class Meta:
        verbose_name = 'Короткая ссылка'
        verbose_name_plural = 'Короткие ссылки'
        ordering = ('id',)

    def __str__(self):
        return self.short_link


class ShoppingCart(FavoriteShoppingCartMixin):

    class Meta(FavoriteShoppingCartMixin.Meta):
        default_related_name = 'cart_recipes'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'

    def __str__(self):
        return f'Рецепт {self.recipe} в корзине пользователя {self.user}'
