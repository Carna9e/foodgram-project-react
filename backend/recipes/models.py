from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
#Carnage dcba4321

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=7)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        verbose_name = 'Тег'  # заголовок писка админки
        verbose_name_plural = 'Теги'  # меню админки
        ordering = ('name',)  # упорядочивание

    def __str__(self):  # вывод
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):  # не все поля
    tags = models.ManyToManyField(Tag)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
        )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='IngredientAmount',
        through_fields=('recipe', 'ingredient')
        )
    name = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to='recipes/images',
        default=None
    )
    text = models.TextField()
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
        )
    #is_favorited = 0
    #is_in_shopping_cart = 0

    # для вывода нескольких значений в админке из-за связи ManyToMany
    def get_tags(self):
        return ", ".join([str(p) for p in self.tags.all()])

    # для вывода нескольких значений в админке из-за связи ManyToMany
    def get_ingredients(self):
        return ", ".join([str(p) for p in self.ingredients.all()])

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-cooking_time',)


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredients',
        on_delete=models.CASCADE
        )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipe_ingredients',
        on_delete=models.CASCADE
        )
    amount = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    # measurement_unit = как вставить сюда значение поля measurement_unit из
    # модели Ingredient чтобы оно отображалось в админке


class FavoritedRecipe(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favorited',
        on_delete=models.CASCADE
    )
    favorited_recipe = models.ForeignKey(
        Recipe,
        related_name='favorited_recipe',
        on_delete=models.CASCADE,
        #null=True
    )

    class Meta:
        constraints = [  # условие уникальности связи пользователя и рецепта
            models.UniqueConstraint(
                fields=('user', 'favorited_recipe'),
                name='unique favourited')]
        verbose_name = 'Избранное'
        # verbose_name_plural = 'Избранные'
        ordering = ('id',)

    #def __str__(self):
    #    return (f'Пользователь: {self.user.username}'
    #            f'рецепт: {self.favorite_recipe.name}')

    # для вывода нескольких значений в админке из-за связи ManyToMany
    def get_favorited_recipe(self):
        return ", ".join([str(p) for p in self.favorited_recipe.all()])


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_shopping_cart'
    )


'''class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscription'
        )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber'
        )
'''


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор')
    created = models.DateTimeField(
        'Дата подписки',
        auto_now_add=True)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription')]

    def __str__(self):
        return (f'Пользователь: {self.user.username},'
                f' автор: {self.author.username}')
