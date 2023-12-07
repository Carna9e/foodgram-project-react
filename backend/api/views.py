from django.db.models import Sum
from django.shortcuts import (get_object_or_404, HttpResponse)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from recipes.models import (Tag, Recipe, Ingredient, ShoppingList,
                            FavoritedRecipe)
from users.models import (User, Subscribe)
from .filters import RecipesFilter
from .mixins import CreateDestroyViewSet
from .paginators import LimitPaginator
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoritedRecipeSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          ShoppingListSerializer, SubscribeListSerializer,
                          SubscribeSerializer, TagSerializer)


class TagViewSet(ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    serializer_class = RecipeSerializer
    filterset_class = RecipesFilter
    pagination_class = LimitPaginator

    def get_queryset(self):
        return Recipe.objects.prefetch_related(
            'recipe_ingredients__ingredient', 'tags'
        ).all()

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
        ingredient_unit = (
            'recipe__recipe_ingredients__ingredient__measurement_unit'
        )
        recipe_amount = 'recipe__recipe_ingredients__amount'
        amount_sum = 'recipe__recipe_ingredients__amount__sum'

        cart = user.shopping_cart.select_related('recipe').values(
            ingredient_name, ingredient_unit).annotate(Sum(
                recipe_amount)).order_by(ingredient_name)
        for selected in cart:
            text += (
                f'{selected[ingredient_name]} ({selected[ingredient_unit]})'
                f' — {selected[amount_sum]}\n'
            )
        response = HttpResponse(text, content_type='text/plain')
        filename = 'shopping_cart.txt'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class FavoritedRecipeViewSet(CreateDestroyViewSet):
    """Добавление и удаление избранных реецептов"""
    serializer_class = FavoritedRecipeSerializer
    View_fun = FavoritedRecipe
    print_string = 'Рецепт не в избранном'


class IngredientViewSet(ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class ShoppingListViewSet(CreateDestroyViewSet):
    """Работа со списком покупок. Удаление/добавление в список покупок."""
    serializer_class = ShoppingListSerializer
    View_fun = ShoppingList
    print_string = 'Рецепта нет в корзине'


class CustomUserViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id):
        data = {'user': request.user.id, 'author': id}
        serializer = SubscribeSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        get_object_or_404(User, id=id)
        if not Subscribe.objects.filter(
                user=request.user, author_id=id).exists():
            return Response({'errors': 'Вы не подписаны на этого автора'},
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
