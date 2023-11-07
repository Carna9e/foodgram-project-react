# Generated by Django 3.2 on 2023-10-31 08:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0024_auto_20231031_1153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favoritedrecipe',
            name='favorited_recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_recipe', to='recipes.recipe'),
        ),
    ]
