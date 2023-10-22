from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe, Tag

User = get_user_model()


class RecipesFilter(FilterSet):

    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = ['is_favorited']

    def get_is_favorited(self, queryset, user, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorited_recipe__user=user)
        return queryset
