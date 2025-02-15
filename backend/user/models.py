from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from foodgram.backend.foodgram_backend.constants import (
    EMAIL_FIELDS_MAX_LENGTH, USER_FIELDS_MAX_LENGTH
)


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

    email = models.EmailField(
        max_length=EMAIL_FIELDS_MAX_LENGTH,
        unique=True,
        verbose_name='Email'
    )
    username = models.CharField(
        max_length=USER_FIELDS_MAX_LENGTH,
        unique=True,
        verbose_name='Юзернейм',
        validators=[
            RegexValidator(
                regex=r'^[w.@+-Z',
                message='Недопустимые символы в юзернейме.'
            )
        ]
    )
    first_name = models.CharField(
        max_length=USER_FIELDS_MAX_LENGTH,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=USER_FIELDS_MAX_LENGTH,
        verbose_name='Фамилия',
    )
    password = models.CharField(
        max_length=USER_FIELDS_MAX_LENGTH,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def clean(self):
        super().clean()
        if self.username.lower() == 'me':
            raise ValidationError('Недопустимое имя пользователя: "me".')


User = get_user_model()


class Follow(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]

    def clean(self):
        """Метод для проверки подписки на самого себя."""
        if self.user == self.author:
            raise ValidationError('Нельзя подписаться на самого себя.')
