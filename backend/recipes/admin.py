from django.contrib import admin

from recipes.models import (
    Tag, Recipe, Ingredient, IngredientAmount,
    ShoppingList, FavoritedRecipe,
    Subscribe
)


class RecipeIngredientInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    readonly_fields = ('id', )
    fields = ('id', 'name', 'color', 'slug')
    #list_editable = ['name', 'color', 'slug'] - изменение объекта в списке
    #search_fields = ('name', 'slug') - поиск
    #list_filter = ('name', 'slug') - фильтр
    #empy_value_display = '-' - для отображения незаполненного поля


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    readonly_fields = ('id', ) # как отобразить поле из параметра другой модели related_name='recipe_ingredients'
    fields = ('id', 'name', 'measurement_unit')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'author', 'get_tags', 'get_ingredients', 'cooking_time'
        )
    readonly_fields = ('id', )
    fields = ('id', 'name', 'author', 'tags', 'text', 'cooking_time', 'image')
    inlines = (RecipeIngredientInline, )  # как вставить сюда ед. измерения ингредиента


@admin.register(FavoritedRecipe)
class FavoritedRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'favorited_recipe'
    )
    search_fields = ('favorited_recipe',)
    list_filter = ('id', 'user', 'favorited_recipe')


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


@admin.register(Subscribe)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display: tuple = (
        'user',
        'author',
    )
    search_fields: tuple = (
        'user',
        'author'
    )
    empty_value_display: str = '-пусто-'
