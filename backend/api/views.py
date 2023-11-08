from django.contrib.auth import get_user_model
from django.shortcuts import HttpResponse
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet


from recipes.models import (Tag, Recipe, Ingredient, ShoppingList,
                            FavoritedRecipe, Subscribe)
from api.serializers import (TagSerializer, RecipeSerializer,
                             RecipeCreateSerializer, IngredientSerializer,
                             ShoppingListSerializer, FavoritedRecipeSerializer,
                             SubscribeSerializer, UserListSerializer,
                             SetPasswordSerializer, UserCreateSerializer)
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated)
from rest_framework import mixins, viewsets
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum
from .filters import RecipesFilter

User = get_user_model()


def index(request):
    return HttpResponse('index')


class LimitPaginator(PageNumberPagination):
    """Кастомная пагинация страниц."""
    page_size_query_param = 'limit'


class CreateDestroyViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    pass


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None  # DontCustomPagination


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filterset_class = RecipesFilter
    pagination_class = LimitPaginator

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'recipe_ingredients__ingredient', 'tags'
        ).all()
        return recipes

    def get_serializer_class(self):

        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        else:
            return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        methods=('get',),
        url_path='download_shopping_cart',
        pagination_class=None)
    def download_file(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(
                'В корзине нет товаров', status=status.HTTP_400_BAD_REQUEST)

        text = 'Список покупок:\n\n'
        ingredient_name = 'recipe__recipe_ingredients__ingredient__name'
        ingredient_unit = (
            'recipe__recipe_ingredients__ingredient__measurement_unit',
        )
        recipe_amount = 'recipe__recipe_ingredients__amount'
        amount_sum = 'recipe__recipe_ingredients__amount__sum'

        cart = user.shopping_cart.select_related('recipe').values(
            ingredient_name, ingredient_unit).annotate(Sum(
                recipe_amount)).order_by(ingredient_name)
        for _ in cart:
            text += (
                f'{_[ingredient_name]} ({_[ingredient_unit]})'
                f' — {_[amount_sum]}\n'
            )
        response = HttpResponse(text, content_type='text/plain')
        filename = 'shopping_cart.txt'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class FavoritedRecipeViewSet(CreateDestroyViewSet):
    """Добавление и удаление избранных реецептов"""
    serializer_class = FavoritedRecipeSerializer

    def get_queryset(self):
        user = self.request.user.id
        return FavoritedRecipe.objects.filter(user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['recipe_id'] = self.kwargs.get('recipe_id')
        return context

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            favorited_recipe=get_object_or_404(
                Recipe,
                id=self.kwargs.get('recipe_id')
            )
        )

    @action(methods=('delete',), detail=True)
    def delete(self, request, recipe_id):
        u = request.user
        if not u.favorited.select_related(
                'favorited_recipe').filter(
                    favorited_recipe_id=recipe_id).exists():
            return Response({'errors': 'Рецепт не в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(
            FavoritedRecipe,
            user=request.user,
            favorited_recipe_id=recipe_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class ShoppingListViewSet(CreateDestroyViewSet):
    """Работа со списком покупок. Удаление/добавление в список покупок."""
    serializer_class = ShoppingListSerializer

    def get_queryset(self):
        user = self.request.user.id
        return ShoppingList.objects.filter(user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['recipe_id'] = self.kwargs.get('recipe_id')
        return context

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            recipe=get_object_or_404(
                Recipe,
                id=self.kwargs.get('recipe_id')
            )
        )

    @action(methods=('delete',), detail=True)
    def delete(self, request, recipe_id):
        u = request.user
        if not u.shopping_cart.select_related(
                'recipe').filter(
                    recipe_id=recipe_id).exists():
            return Response({'errors': 'Рецепта нет в корзине'},
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(
            ShoppingList,
            user=request.user,
            recipe=recipe_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomUserViewSet(UserViewSet):
    """Создаие подписок"""

    def get_serializer_class(self):
        if self.action == 'set_password':
            return SetPasswordSerializer
        if self.action == 'create':
            return UserCreateSerializer
        return UserListSerializer

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        queryset = User.objects.filter(signed__user=request.user)
        print(queryset)
        pages = self.paginate_queryset(queryset)
        print(pages)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request},)
        return self.get_paginated_response(serializer.data)


class SubscribeViewSet(CreateDestroyViewSet):
    """Получение списка всех подписок на пользователей."""
    serializer_class = SubscribeSerializer
    pagination_class = LimitPaginator

    def get_queryset(self):
        return self.request.user.subscriber.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['author_id'] = self.kwargs.get('user_id')
        print(context)
        return context

    def create(self, request, *args, **kwargs):
        user = self.request.user
        author = get_object_or_404(
            User,
            id=self.kwargs.get('user_id')
        )
        serializer = self.get_serializer(
            author,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        Subscribe.objects.create(user=user, author=author)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=('delete',), detail=True)
    def delete(self, request, user_id):
        get_object_or_404(User, id=user_id)
        if not Subscribe.objects.filter(
                user=request.user, author_id=user_id).exists():
            return Response({'errors': 'Вы не подписаны на автора'},
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(
            Subscribe,
            user=request.user,
            author_id=user_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
