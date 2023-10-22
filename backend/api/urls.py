"""foodgram URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from rest_framework import routers
from django.urls import path, include

from api.views import (index, CustomUserViewSet, TagViewSet, RecipeViewSet,
                       IngredientViewSet, ShoppingCartViewSet,
                       FavoritedRecipeViewSet, SubscribeViewSet)

from django.conf import settings  # брать картинки из директории, указанной в MEDIA_ROOT
from django.conf.urls.static import static  # брать картинки из директории, указанной в MEDIA_ROOT

#app_name = 'api'

router = routers.DefaultRouter()
router.register('users', CustomUserViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)
router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart', ShoppingCartViewSet,
    basename='shoppingcart')
#router.register(
#    r'recipes/(?P<recipe_id>\d+)/favorite', RecipeViewSet,
#    basename='favorited')
'''router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite', FavoritedRecipeViewSet,
    basename='favorited')'''
router.register(
    r'users/(?P<user_id>\d+)/subscribe', SubscribeViewSet,
    basename='subscribe')

urlpatterns = [
    path('index', index),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]

#if settings.DEBUG:  # будет работать, когда ваш сайт в режиме отладки.
    # позволяет обращаться к файлам в директории, указанной в MEDIA_ROOT
    # по имени, через префикс MEDIA_URL
#    urlpatterns += static(settings.MEDIA_URL,
#                         document_root=settings.MEDIA_ROOT)
