from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import models

from api.validators import validate_username
from foodgram_backend import constants


class User(AbstractUser):
    username = models.CharField(
        verbose_name='username',
        max_length=constants.USERNAME_LENGTH,
        unique=True,
        validators=(
            RegexValidator(constants.REGEX_USERNAME),
            validate_username,
        )
    )
    email = models.EmailField(
        verbose_name='email',
        max_length=constants.EMAIL_LENGTH,
        unique=True,
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        blank=True,
        null=True,
        upload_to='avatars'
    )
    is_subscribed = models.ManyToManyField(
        to='self',
        verbose_name='Подписка',
        related_name='subscribers',
        symmetrical=False,
        blank=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username[:constants.USERNAME_CUT]
