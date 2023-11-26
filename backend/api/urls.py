from django.urls import path, include
from rest_framework import routers

from .views import (index, CustomUserViewSet, FavoritedRecipeViewSet,
                    IngredientViewSet, RecipeViewSet, ShoppingListViewSet,
                    SubscribeViewSet, TagViewSet)


router = routers.DefaultRouter()
router.register('users', CustomUserViewSet)
#router.register(r'users', CustomUserViewSet, basename='users')
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)


router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart', ShoppingListViewSet,
    basename='shoppingcart')
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite', FavoritedRecipeViewSet,
    basename='favorited')
router.register(
    r'users/(?P<user_id>\d+)/subscribe', SubscribeViewSet,
    basename='subscribe')

urlpatterns = [
    path('index', index),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]

# if settings.DEBUG:  # будет работать, когда ваш сайт в режиме отладки.
# позволяет обращаться к файлам в директории, указанной в MEDIA_ROOT
# по имени, через префикс MEDIA_URL
#    urlpatterns += static(settings.MEDIA_URL,
#                         document_root=settings.MEDIA_ROOT)
