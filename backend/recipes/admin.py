from django.contrib import admin

from .models import (FavoritedRecipe, Ingredient, IngredientAmount,
                     Recipe, ShoppingList, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    readonly_fields = ('id', )
    fields = ('id', 'name', 'color', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    readonly_fields = ('id', )
    fields = ('id', 'name', 'measurement_unit')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    # для вывода нескольких значений в админке из-за связи ManyToMany
    @admin.display(description="Теги")
    def get_tags(self, obj):
        return ", ".join([str(p) for p in obj.tags.all()])

    @admin.display(description="Ингредиенты")
    def get_ingredients(self, obj):
        return ", ".join([str(p) for p in obj.ingredients.all()])

    list_display = (
        'id', 'name', 'author', 'get_tags', 'get_ingredients', 'cooking_time',
        'pub_date'
    )
    readonly_fields = ('id', )
    list_filter = ('name', 'author', 'tags', 'pub_date')
    fields = ('id', 'name', 'author', 'tags', 'text', 'cooking_time', 'image')
    inlines = (RecipeIngredientInline, )
    # как вставить сюда ед. измерения ингредиента


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
