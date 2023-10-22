# Generated by Django 3.2 on 2023-09-16 22:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20230916_0202'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favoriterecipe',
            options={'ordering': ('id',), 'verbose_name': 'Избранный рецепт', 'verbose_name_plural': 'Избранные рецепты'},
        ),
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ('name',), 'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('-cooking_time',), 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ('name',), 'verbose_name': 'Тег', 'verbose_name_plural': 'Теги'},
        ),
    ]
