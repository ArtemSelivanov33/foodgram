from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet

from utils.text_constants import ErrorMessage
from .serializers import FavoriteSerializer


class FavoriteViewSet(GenericViewSet, CreateModelMixin, DestroyModelMixin):
    """Класс представления для работы с избранными записями."""

    def favorite(self, request, pk, model_to_add, model_to_serialize):
        """Добавление записи в избранное или удаление из избранного."""
        user = request.user
        recipe = get_object_or_404(model_to_serialize, id=pk)
        serializer = FavoriteSerializer(
            data={'user': user.id, 'recipe': recipe.id}
        )
        if serializer.is_valid():
            if request.method == 'POST':
                if not model_to_add.objects.filter(
                    user=user, recipe=recipe
                ).exists():
                    serializer.save()
                    return Response(
                        serializer.data, status=status.HTTP_201_CREATED
                    )
                return Response({'errors': ErrorMessage.ADD_ENTRY_ERROR},
                                status=status.HTTP_400_BAD_REQUEST)
            if model_to_add.objects.filter(user=user, recipe=recipe).exists():
                model_to_add.objects.filter(user=user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': ErrorMessage.NO_ENTRY},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
