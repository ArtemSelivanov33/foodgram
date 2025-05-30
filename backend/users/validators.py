from django.core.exceptions import ValidationError


def validate_username_me(value):
    if value.lower() == 'me':
        raise ValidationError(
            'Пользователь с именем "me" не может зарегистрироваться.',
            code='invalid_username',
        )
