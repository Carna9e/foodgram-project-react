import base64
from django.core.files.base import ContentFile
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

from recipes.models import (Tag, Recipe, IngredientAmount, Ingredient,
                            FavoritedRecipe, ShoppingCart, Subscription)#, Subscribe)
from djoser.serializers import (PasswordSerializer, UserSerializer,
                                UserCreateSerializer)


User = get_user_model()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


###
class SetPasswordSerializer(PasswordSerializer):
    current_password = serializers.CharField(
        required=True,
        label='Текущий пароль')

    def validate(self, data):
        user = self.context.get('request').user
        if data['new_password'] == data['current_password']:
            raise serializers.ValidationError({
                "new_password": "Пароли не должны совпадать"})
        check_current = check_password(data['current_password'], user.password)
        if check_current is False:
            raise serializers.ValidationError({
                "current_password": "Введен неверный пароль"})
        return data


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
                and Subscription.objects.filter(
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


class SubscribeRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(UserListSerializer):
    
    #is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(
        source='author.recipe.count')

    class Meta(UserListSerializer.Meta):
    #class Meta():
        '''model = Subscribe
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count',)'''
        model = User
        fields = UserListSerializer.Meta.fields + ('recipes', 'recipes_count')
        read_only_fields = ('email', 'username')

    def validate(self, data):
        user = self.context.get('request').user
        author = self.context.get('author_id')
        if user.id == int(author):
            raise serializers.ValidationError({
                'errors': 'Нельзя подписаться на самого себя'})
        #if Subscribe.objects.filter(user=user, author=author).exists():
        if User.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError({
                'errors': 'Вы уже подписаны на данного пользователя'})
        return data

    def get_recipes(self, obj):
        recipes = obj.author.recipes.all()
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        return SubscribeRecipeSerializer(
            recipes,
            many=True).data

    def get_is_subscribed(self, obj):
        #subscribe = Subscribe.objects.filter(
        subscribe = User.objects.filter(
            user=self.context.get('request').user,
            author=obj.author
        )
        if subscribe:
            return True
        return False
###


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='ingredient.id')  # ReadOnlyField тип
    name = serializers.CharField(source='ingredient.name')  # ReadOnlyField тип
    measurement_unit = serializers.CharField(  # ReadOnlyField тип
        source='ingredient.measurement_unit'
        )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    #author = CustomUserSerializer()
    author = UserListSerializer()
    ingredients = IngredientAmountSerializer(
        many=True,
        source='recipe_ingredients' #='recipeingredient_set'
        )
    # ingredients = serializers.SerializerMethodField()

    # def get_ingredients(self, instance):
    #    return RecipeIngredientSerializer(
    #        instance.recipe_ingredients.all(),
    #        many=True
    #    ).data
    is_favorited = serializers.SerializerMethodField()
    #is_in_shopping_cart = serializers.SerializerMethodField()
    
###
    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited', 'name',
            'image', 'text', 'cooking_time')  # 'is_in_shopping_cart',

    def get_is_favorited(self, obj):
        return (self.context.get('request').user.is_authenticated
                and FavoritedRecipe.objects.filter(
                    user=self.context.get('request').user,
                    favorited_recipe=obj
        ).exists())

    '''def get_is_in_shopping_cart(self, obj):
        return (self.context.get('request').user.is_authenticated
                and ShoppingCart.objects.filter(
                    user=self.context.get('request').user,
                    recipe=obj
        ).exists())'''
###


class FavoritedRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='favorited_recipe.id',  # Recipe.id models.py стр.97
    )
    name = serializers.ReadOnlyField(
        source='favorited_recipe.name',
    )
    image = serializers.CharField(
        source='favorited_recipe.image',
        read_only=True,
    )
    cooking_time = serializers.ReadOnlyField(
        source='favorited_recipe.cooking_time',
    )

    class Meta:
        model = FavoritedRecipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = self.context.get('request').user
        recipe = self.context.get('recipe_id')
        if FavoritedRecipe.objects.filter(user=user,
                                          favorited_recipe=recipe).exists():
            raise serializers.ValidationError({
                'errors': 'Рецепт уже в избранном'})
        return data


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = RecipeIngredientCreateSerializer(many=True) #source можно попробовать

    class Meta:
        model = Recipe
        fields = ('name', 'cooking_time', 'text', 'image', 'tags',
                  'ingredients')

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance = super().create(validated_data)

        create_ingredients = [
            IngredientAmount(
                recipe=instance,
                ingredient=ingredients_data['ingredient'],
                amount=ingredients_data['amount']
            )
            for ingredients_data in ingredients
        ]
        IngredientAmount.objects.bulk_create(
            create_ingredients
        )

        #for ingredients_data in ingredients:# плохо каждый раз по запросу. нужен бал create 2:27
        #    IngredientAmount(
        #        recipe=instance,
        #        ingredient=ingredients_data['ingredient'],
        #        amount=ingredients_data['amount']
        #    ).save()

        return instance

    def to_representation(self, instance):
        #2:25 и 2:30 ????
        #recipe = RecipeSerializer(
        #    instance.recipe.all(),
        #    many=True
        #).data 

        #tags = TagSerializer(instance.tags.all(), many=True).data
        #ingredients = RecipeSerializer(IngredientAmount.ingredients.all(), many=True).data
       
        '''return {
            'ingredients': ingredients,
            #'tags': tags,
            #'ingredients': 'ingredients'
        }'''
        return RecipeSerializer(instance, context=self.context).data
    
    #def update(self, instance, validated_data): !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        

'''
class FavoritedRecipeSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='favorited_recipe.id')
    name = serializers.CharField(source='favorited_recipe.name')
    image = serializers.CharField(
        source='favorited_recipe.image',
        read_only=True,
    )
    cooking_time = serializers.CharField(
        source='favorited_recipe.cooking_time')

    class Meta:
        model = FavoritedRecipe  #IngredientAmount
        fields = ('id', 'name', 'image', 'cooking_time')
'''
###


class ShoppingCartSerializer(serializers.ModelSerializer):
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
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = self.context.get('request').user
        recipe = self.context.get('recipe_id')
        if ShoppingCart.objects.filter(user=user,
                                       recipe=recipe).exists():
            raise serializers.ValidationError({
                'errors': 'Рецепт уже добавлен в список покупок'})
        return data
