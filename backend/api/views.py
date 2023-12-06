from django.db.models import Sum
from django.shortcuts import (get_object_or_404, HttpResponse)
from rest_framework import mixins, viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from recipes.models import (Tag, Recipe, Ingredient, ShoppingList,
                            FavoritedRecipe)
from users.models import (User, Subscribe)

from .filters import RecipesFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoritedRecipeSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          ShoppingListSerializer, SubscribeListSerializer,
                          SubscribeSerializer, TagSerializer)


class LimitPaginator(PageNumberPagination):
    """Кастомная пагинация страниц."""
    page_size_query_param = 'limit'


class CreateDestroyViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    pass


class TagViewSet(ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None  # DontCustomPagination


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
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
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        methods=('get',),
        url_path='download_shopping_cart',
        pagination_class=None,
        permission_classes=(IsAuthenticated,)
    )
    def download_file(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(
                'В корзине нет товаров', status=status.HTTP_400_BAD_REQUEST)

        text = 'Список покупок:\n\n'
        ingredient_name = 'recipe__recipe_ingredients__ingredient__name'
        ingredient_unit = 'recipe__recipe_ingredients__ingredient__measurement_unit'
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
        if not request.user.favorited.select_related(
                'favorited_recipe').filter(
                    favorited_recipe_id=recipe_id).exists():
            return Response({'errors': 'Рецепт не в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)

        FavoritedRecipe.objects.get(
            user=request.user,
            favorited_recipe_id=recipe_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
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
        if not request.user.shopping_cart.select_related(
                'recipe').filter(
                    recipe_id=recipe_id).exists():
            return Response({'errors': 'Рецепта нет в корзине'},
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(
            ShoppingList,
            user=request.user,
            recipe=recipe_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomUserViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id):

        author = get_object_or_404(User, pk=id)
        user = request.user
        subscriptions = request.user.subscriber.filter(
            user=user,
            author=author
        )
        if subscriptions.exists():
            message = 'Данная подписка уже существует!'
            return Response(
                {'detail': message},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            message = 'Нельзя подписаться на самого себя!'
            return Response(
                {'detail': message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = {'user': request.user.id, 'author': id}
        serializer = SubscribeSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        get_object_or_404(User, id=id)
        if not Subscribe.objects.filter(
                user=request.user, author_id=id).exists():
            return Response({'errors': 'Вы не подписаны на автора'},
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(
            request.user.subscriber.filter(author_id=id)).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeViewSet(ListAPIView):
    pagination_class = LimitPaginator
    permission_classes = [IsAuthenticated]
    serializer_class = SubscribeListSerializer

    def get_queryset(self):
        return User.objects.filter(signed__user=self.request.user)
