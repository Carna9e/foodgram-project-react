from django.urls import path, include
from rest_framework import routers

from .views import (CustomUserViewSet, FavoritedRecipeViewSet,
                    IngredientViewSet, RecipeViewSet, ShoppingListViewSet,
                    SubscribeViewSet, TagViewSet)

app_name = 'api'

router = routers.DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')

router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart', ShoppingListViewSet,
    basename='shoppingcart')
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite', FavoritedRecipeViewSet,
    basename='favorited')

urlpatterns = [
    path('users/<int:id>/subscribe/', CustomUserViewSet.as_view(),
         name='subscribe'),
    path('users/subscriptions/', SubscribeViewSet.as_view(),
         name='subscriptions'),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    path('', include(router.urls))
]
