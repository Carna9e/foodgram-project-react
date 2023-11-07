from django.db import models
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
#Carnage dcba4321

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=200, verbose_name='Тег')
    color = models.CharField(max_length=7, verbose_name='Цвет')
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        verbose_name = 'Тег'  # заголовок списка админки
        verbose_name_plural = 'Теги'  # меню админки
        ordering = ('name',)  # упорядочивание

    def __str__(self):  # вывод
        return (f'Тег  {self.name}')


class Ingredient(models.Model):
    name = models.CharField(verbose_name='Ингредиент', max_length=200)
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return (f'Ингредиент {self.name}')


class Recipe(models.Model):  # не все поля
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
        max_length=200,
        verbose_name='Название'
        )
    image = models.ImageField(
        upload_to='recipes/images',
        default=None,
        verbose_name='Изображение'
        )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления'
        )

    # для вывода нескольких значений в админке из-за связи ManyToMany
    @admin.display(description="Теги")
    def get_tags(self):
        return ", ".join([str(p) for p in self.tags.all()])

    # для вывода нескольких значений в админке из-за связи ManyToMany
    @admin.display(description="Ингредиенты")
    def get_ingredients(self):
        return ", ".join([str(p) for p in self.ingredients.all()])

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-cooking_time',)

    def __str__(self):  # вывод
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
        validators=[MinValueValidator(1)],
        verbose_name='Количество'
        )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ('id',)
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique ingredient'),)

    def __str__(self):
        return (f'В рецепте {self.recipe.name} {self.amount} '
                f'{self.ingredient.measurement_unit} {self.ingredient.name}')
    # measurement_unit = как вставить сюда значение поля measurement_unit из
    # модели Ingredient чтобы оно отображалось в админке


class FavoritedRecipe(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favorited',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    favorited_recipe = models.ForeignKey(
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
            models.UniqueConstraint(  # условие уникальности связи пользователя и рецепта
                fields=('user', 'favorited_recipe'),
                name='unique favourited'),
                )


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        #related_name='follower',
        verbose_name='Подписчик'
        )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='signed',
        #related_name='following',
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
