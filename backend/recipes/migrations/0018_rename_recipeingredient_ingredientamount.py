# Generated by Django 3.2 on 2023-10-11 11:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0017_alter_favoritedrecipe_favorited_recipe'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RecipeIngredient',
            new_name='IngredientAmount',
        ),
    ]
