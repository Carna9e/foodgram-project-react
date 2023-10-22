from django.contrib import admin

from recipes.models import (Tag, Recipe, Ingredient, IngredientAmount,
                            ShoppingCart, FavoritedRecipe,
                            ) #Subscription, 


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
    #empy_value_display = '-пусто-' - для отображения незаполненного поля


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    readonly_fields = ('id', ) # как отобразить поле из параметра другой модели related_name='recipe_ingredients'
    fields = ('id', 'name', 'measurement_unit')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'author', 'get_tags', 'get_ingredients',
        'cooking_time'
        )
    readonly_fields = ('id', )
    fields = ('id', 'name', 'author', 'tags', 'text', 'cooking_time', 'image')  # , 'favorited_recipe'
    inlines = (RecipeIngredientInline, ) # как вставить сюда ед. измерения ингредиента


@admin.register(FavoritedRecipe)
class FavoritedRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'favorited_recipe'
    )
    search_fields = ('favorited_recipe',)
    list_filter = ('id', 'user', 'favorited_recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    pass


'''@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    pass'''
