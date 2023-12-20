from django.shortcuts import get_object_or_404
from rest_framework import (mixins, viewsets, status)
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Recipe


class CreateDestroyViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):

    def get_queryset(self, name_model):
        user_id = self.request.user.id
        return name_model.objects.filter(user=user_id)

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
        if not self.name_model.objects.filter(
                recipe_id=recipe_id).exists():
            return Response({'errors': self.print_string},
                            status=status.HTTP_400_BAD_REQUEST)

        self.name_model.objects.get(
            user=request.user,
            recipe_id=recipe_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
