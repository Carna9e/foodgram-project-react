# Generated by Django 3.2.16 on 2023-12-07 22:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoppinglist',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(through='recipes.IngredientAmount', to='recipes.Ingredient'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(to='recipes.Tag', verbose_name='Теги'),
        ),
        migrations.AddField(
            model_name='ingredientamount',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredients', to='recipes.ingredient', verbose_name='Ингредиент'),
        ),
        migrations.AddField(
            model_name='ingredientamount',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredients', to='recipes.recipe'),
        ),
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.UniqueConstraint(fields=('name', 'measurement_unit'), name='unique ingredient'),
        ),
        migrations.AddField(
            model_name='favoritedrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_recipe', to='recipes.recipe', verbose_name='Рецепт'),
        ),
        migrations.AddField(
            model_name='favoritedrecipe',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddConstraint(
            model_name='shoppinglist',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique recipe in shopping cart'),
        ),
        migrations.AddConstraint(
            model_name='ingredientamount',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique ingredient amount'),
        ),
        migrations.AddConstraint(
            model_name='favoritedrecipe',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique favourited'),
        ),
    ]
