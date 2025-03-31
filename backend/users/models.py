from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from foodgram_backend import constants


class User(AbstractUser):
    username = models.CharField(
        verbose_name='username',
        max_length=constants.USERNAME_LENGTH,
        unique=True,
        validators=(UnicodeUsernameValidator(),)
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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username[:constants.USERNAME_CUT]
