
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from recipes.constants import UserConstants

from .validators import validate_username, validate_name


class User(AbstractUser):
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        help_text='Укажите адрес электронной почты!',
        max_length=UserConstants.USER_EMAIL_LENGTH,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Логин пользователя',
        help_text='Укажите логин!',
        max_length=UserConstants.USER_CREDENTIALS_MAX_LENGTH,
        unique=True,
        validators=(
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Имя пользователя содержит недопустимые символы.',
            ),
            validate_username
        ),
    )
    first_name = models.CharField(
        verbose_name='Имя пользователя',
        help_text='Укажите имя!',
        max_length=UserConstants.USER_CREDENTIALS_MAX_LENGTH,
        validators=(validate_name,),
    )
    last_name = models.CharField(
        verbose_name='Фамилия пользователя',
        help_text='Укажите фамилию!',
        max_length=UserConstants.USER_CREDENTIALS_MAX_LENGTH,
        validators=(validate_name,),
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_user',),
        ]
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='signed',
        verbose_name='Автор'
    )
    created = models.DateTimeField(
        'Дата подписки',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-id',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription'),)

    def __str__(self):
        return (f'Подписка пользователя {self.user.username}'
                f' на пользователя {self.author.username}')
