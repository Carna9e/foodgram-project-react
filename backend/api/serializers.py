
from django.core.validators import MinValueValidator, MaxValueValidator
from djoser.serializers import (UserCreateSerializer, UserSerializer)
from rest_framework import serializers

from recipes.constants import (MAX_COOKING_TIME, MIN_VALUE)
from recipes.models import (Tag, Recipe, IngredientAmount, Ingredient,
                            FavoritedRecipe, ShoppingList)
from users.models import (User, Subscribe)
from .fields import Base64ImageField


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class UserListSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        return (self.context.get('request').user.is_authenticated
                and Subscribe.objects.filter(
                    user=self.context.get('request').user,
                    author=obj
        ).exists())


class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')
        required_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ('user', 'author')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def validate(self, data):
        user = data['user']
        author = data['author']
        if user == author:
            raise serializers.ValidationError({
                'errors': 'Нельзя подписаться на себя самого!'})
        if Subscribe.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError({
                'errors': 'Вы уже подписаны на данного пользователя'})
        return data

    def to_representation(self, instance):
        return SubscribeListSerializer(
            instance.author, context=self.context
        ).data


class SubscribeRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeListSerializer(UserListSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(
        source='recipe.count')

    class Meta(UserListSerializer.Meta):
        fields = UserListSerializer.Meta.fields + (
            'id', 'recipes', 'recipes_count'
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return
        limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            try:
                recipes = recipes[:int(limit)]
            except TypeError:
                raise serializers.ValidationError({
                    'errors': 'Ошибка несоответствия типов!'
                })
        return SubscribeRecipeSerializer(
            recipes, many=True, context=self.context
        ).data


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserListSerializer()
    ingredients = IngredientAmountSerializer(
        many=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited', 'name',
            'image', 'text', 'cooking_time', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        return (self.context.get('request').user.is_authenticated
                and FavoritedRecipe.objects.filter(
                    user=self.context.get('request').user,
                    recipe=obj
        ).exists())

    def get_is_in_shopping_cart(self, obj):
        return (self.context.get('request').user.is_authenticated
                and ShoppingList.objects.filter(
                    user=self.context.get('request').user,
                    recipe=obj
        ).exists())


class FavoritedRecipeSerializer(SubscribeRecipeSerializer):
    id = serializers.ReadOnlyField(
        source='recipe.id',
    )
    name = serializers.ReadOnlyField(
        source='recipe.name',
    )
    image = serializers.CharField(
        source='recipe.image',
        read_only=True,
    )
    cooking_time = serializers.ReadOnlyField(
        source='recipe.cooking_time',
    )

    class Meta:
        model = FavoritedRecipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = self.context.get('request').user
        recipe = self.context.get('recipe_id')
        if FavoritedRecipe.objects.filter(user=user,
                                          recipe=recipe).exists():
            raise serializers.ValidationError({
                'errors': 'Рецепт уже находится в избранном'})
        return data


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    def validate(self, data):
        amount = data.get('amount')
        if amount < 1:
            raise serializers.ValidationError({
                'amount': 'Минимальное количество ингридиента - 1'
            })
        return data

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = RecipeIngredientCreateSerializer(many=True)
    cooking_time = serializers.IntegerField(
        validators=(
            MinValueValidator(MIN_VALUE),
            MaxValueValidator(MAX_COOKING_TIME)
        ),
    )

    class Meta:
        model = Recipe
        fields = ('name', 'cooking_time', 'text', 'image', 'tags',
                  'ingredients')

    def validate(self, data):
        ingredients = data.get('ingredients')
        for ingredient in ingredients:
            if not Ingredient.objects.filter(id=ingredient['id']).exists():
                raise serializers.ValidationError({
                    'ingredients': f'Ингредиента с id - {ingredient["id"]} нет'
                })
        if len(ingredients) != len(set([item['id'] for item in ingredients])):
            raise serializers.ValidationError(
                'Такой ингредиент уже есть!')
        tags = data.get('tags')
        if len(tags) != len(set([item for item in tags])):
            raise serializers.ValidationError({
                'tags': 'Тэги не должны повторяться!'})
        return data

    def create_ingredients(self, instance, ingredients):
        create_ingredients = [
            IngredientAmount(
                recipe=instance,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
            for ingredient in ingredients
        ]
        IngredientAmount.objects.bulk_create(
            create_ingredients
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance = super().create(validated_data)
        self.create_ingredients(instance, ingredients)
        return instance

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(instance, ingredients)
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags'))
        return super().update(
            instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class ShoppingListSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='recipe.id',
    )
    name = serializers.ReadOnlyField(
        source='recipe.name',
    )
    image = serializers.CharField(
        source='recipe.image',
        read_only=True,
    )
    cooking_time = serializers.ReadOnlyField(
        source='recipe.cooking_time',
    )

    class Meta:
        model = ShoppingList
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = self.context.get('request').user
        recipe = self.context.get('recipe_id')
        if ShoppingList.objects.filter(user=user,
                                       recipe=recipe).exists():
            raise serializers.ValidationError({
                'errors': 'Рецепт уже добавлен в список покупок'})
        return data
