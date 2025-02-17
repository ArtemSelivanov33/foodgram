from django.urls import include, path
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientViewSet, RecipeViewSet, TagViewset, UserListViewSet
)

app_name = 'api'

router = DefaultRouter()
router.register('tags', TagViewset, basename='tag')
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('users', UserListViewSet, basename='user')


urlpatterns = [
    path('auth/token/login/', TokenCreateView.as_view(), name='token_login'),
    path(
        'auth/token/logout/', TokenDestroyView.as_view(), name='token_logout'
    ),
    path('', include(router.urls)),
    path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken'))
]
