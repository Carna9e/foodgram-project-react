from colorfield.fields import ColorField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from users.models import User
from .constants import RecipeConstants


class Tag(models.Model):
    name = models.CharField(
        max_length=RecipeConstants.MAX_STR_LENGTH,
        verbose_name='Тег',
        unique=True
    )
    color = ColorField(
        default='#FF0000',
        verbose_name='Цвет',
        unique=True,
        help_text='Цвет тэга в формате HEX, например: #FF0000.'
    )
    slug = models.SlugField(
        max_length=RecipeConstants.MAX_STR_LENGTH,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return (f'{self.name}')


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Ингредиент',
        max_length=RecipeConstants.MAX_STR_LENGTH
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=RecipeConstants.MAX_STR_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique ingredient'),
        )

    def __str__(self):
        return (f'{self.name}')


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='IngredientAmount',
        through_fields=('recipe', 'ingredient')
    )
    name = models.CharField(
        max_length=RecipeConstants.MAX_STR_LENGTH,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='recipes/images',
        default=None,
        verbose_name='Изображение'
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(
        validators=(
            MinValueValidator(RecipeConstants.MIN_VALUE),
            MaxValueValidator(RecipeConstants.MAX_COOKING_TIME)
        ),
        verbose_name='Время приготовления'
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return (f'Рецепт  {self.name} пользователя {self.author}')


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredients',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipe_ingredients',
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(RecipeConstants.MIN_VALUE)],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ('id',)
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique ingredient amount'),
        )

    def __str__(self):
        return (f'В рецепте {self.recipe.name} {self.amount} '
                f'{self.ingredient.measurement_unit} {self.ingredient.name}')


class FavoritedRecipe(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favorited',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorited_recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('id',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique favourited'),
        )


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        ordering = ('id',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique recipe in shopping cart'),)

    def __str__(self):
        return (f'Рецепт "{self.recipe.name}" в'
                f' списке покупок пользователя {self.user.username}.')
