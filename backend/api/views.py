from django.contrib.auth import get_user_model
from django.shortcuts import HttpResponse
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet


from recipes.models import (Tag, Recipe, Ingredient, ShoppingCart,
                            FavoritedRecipe, Subscribe)
from api.serializers import (TagSerializer, RecipeSerializer,
                             RecipeCreateSerializer, IngredientSerializer,
                             ShoppingCartSerializer, FavoritedRecipeSerializer,
                             SubscribeSerializer, UserListSerializer,
                             SetPasswordSerializer, UserCreateSerializer)
# UserListSerializer, SetPasswordSerializer, UserCreateSerializer,


##
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated, IsAuthenticatedOrReadOnly)
from rest_framework import mixins, viewsets
from rest_framework.pagination import PageNumberPagination

from .filters import RecipesFilter

User = get_user_model()


class CustomPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'


def index(request):
    return HttpResponse('index')


#class CustomUserViewSet(UserViewSet):
#    pass


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination  ###
    serializer_class = RecipeSerializer
    filterset_class = RecipesFilter

    '''def dispatch(self, request, *args, **kwargs):
        res = super().dispatch(request, *args, **kwargs)

        from django.db import connection
        print(len(connection.queries))
        for q in connection.queries:
            print('>>>>', q['sql'])

        return res'''

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'recipe_ingredients__ingredient', 'tags'
        ).all()
        return recipes

    def get_serializer_class(self):
        #if self.action == 'create': # сложнее надо: апдейт сериалайзера  1:45
        #    return RecipeCreateSerializer
        #return RecipeSerializer

        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        #elif self.action in ('shoping_cart', 'favorite'):
        #    return RecipeMinifieldSerializer
        else:
            return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


### говнецо
    '''@action(
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
        ingredient_name = 'recipe__recipe__ingredient__name'
        ingredient_unit = 'recipe__recipe__ingredient__measurement_unit'
        recipe_amount = 'recipe__recipe__amount'
        amount_sum = 'recipe__recipe__amount__sum'
        cart = user.shopping_cart.select_related('recipe').values(
            ingredient_name, ingredient_unit).annotate(Sum(
                recipe_amount)).order_by(ingredient_name)
        for _ in cart:
            text += (
                f'{_[ingredient_name]} ({_[ingredient_unit]})'
                f' — {_[amount_sum]}\n'
            )
        response = HttpResponse(text, content_type='text/plain')
        filename = 'shopping_list.txt'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response'''

###


class CreateDestroyViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    pass


class FavoritedRecipeViewSet(CreateDestroyViewSet):
    """Работа с избранными рецептами.
        Удаление/добавление в избранное."""
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

###


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class ShoppingCartViewSet(CreateDestroyViewSet):
    """Работа со списком покупок. Удаление/добавление в список покупок."""
    serializer_class = ShoppingCartSerializer

    def get_queryset(self):
        user = self.request.user.id
        return ShoppingCart.objects.filter(user=user)

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
            ShoppingCart,
            user=request.user,
            recipe=recipe_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeViewSet(CreateDestroyViewSet):
    """Получение списка всех подписок на пользователей."""
    serializer_class = SubscribeSerializer

    def get_queryset(self):
        return self.request.user.follower.all()

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
        Subscribe.objects.create(
            user=user,
            author=author
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def perform_create(self, serializer):
    #     print(self.request.user)
        # serializer.save(
        #     user=self.request.user,
        #     author=get_object_or_404(
        #         User,
        #         id=self.kwargs.get('user_id')
        #     )
        # )

    @action(methods=('delete',), detail=True)
    def delete(self, request, user_id):
        get_object_or_404(User, id=user_id)
        if not Subscribe.objects.filter(
                user=request.user, author_id=user_id).exists():
            return Response({'errors': 'Вы не были подписаны на автора'},
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(
            Subscribe,
            user=request.user,
            author_id=user_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomUserViewSet(UserViewSet):
    """Создание/удаление подписки на пользователя."""
    # permission_classes = (IsAuthenticatedOrReadOnly,)

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
        queryset = User.objects.filter(following__user=request.user)
        print(queryset)
        pages = self.paginate_queryset(queryset)
        print(pages)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request},)
        return self.get_paginated_response(serializer.data)
