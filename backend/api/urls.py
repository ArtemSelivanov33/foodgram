from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    AuthToken, IngredientViewSet, RecipeViewSet, TagViewset, UserListViewSet
)

app_name = 'api'

router = DefaultRouter()
router.register('tags', TagViewset, basename='tag')
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('users', UserListViewSet, basename='user')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/token/login/', AuthToken.as_view(), name='login'),
]
