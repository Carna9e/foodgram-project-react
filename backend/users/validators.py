import re
from django.core.exceptions import ValidationError


def validate_username(value):
    if value == 'me':
        return ValidationError('Недопустимое имя пользователя.')
    return value


def validate_name(value):
    """Валидация name на корректность."""
    if not re.match(r'^[а-яА-ЯёЁa-zA-Z\s]+$', value):
        raise ValidationError(
            'Введены некорректные символы!'
        )
    return value
