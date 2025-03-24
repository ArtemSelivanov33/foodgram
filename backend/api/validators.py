from django.core.exceptions import ValidationError


def validate_username(value):
    if value.lower() == 'me':
        raise ValidationError(
            ('Пользователь с именем "me" не может зарегистрироваться.'),
            code='invalid_username',
        )


def validate_not_self_subscription(value):
    if value.filter(pk=value.instance.pk).exists():
        raise ValidationError("Нельзя подписаться на самого себя.")
