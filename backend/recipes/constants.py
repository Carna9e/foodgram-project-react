from enum import Enum


class RecipeConstants(Enum):
    #ADMIN_EMPTY_VALUE = 'Не задано'
    #FAVORITES_DESCRIPTION = 'В избранном'
    #INGREDIENTS_DESCRIPTION = 'Ингредиенты'
    #IMAGE_DESCRIPTION = 'Изображение'
    MAX_STR_LENGTH = 200  #
    TAG_COLOR_LENGTH = 7  #
    #STR_RETURN_VALUE = 30
    MAX_COOKING_TIME = 300 #
    #MAXIMUM_AMOUNT_ALLOWED = 10000
    MIN_VALUE = 1  #


class UserConstants(Enum):
    USER_CREDENTIALS_MAX_LENGTH = 150  #
    USER_EMAIL_LENGTH = 254  #
    #STR_RETURN_VALUE = 30
    #RECIPES_AMOUNT = 'Количество рецептов'
    #SUBSCRIBERS_AMOUNT = 'Количество подписчиков'
