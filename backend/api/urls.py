from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CustomUserViewSet,
    IngredientViewSet,
    RecipeViewSet,
    TagViewset,
    UserListViewSet
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
    path('api/users/', CustomUserViewSet.as_view(), name='register'),
    path(
        'auth/token/login/',
        CustomUserViewSet.as_view({'post': 'post_token'}),
        name='token_login'
    ),
    path(
        'auth/token/logout/',
        CustomUserViewSet.as_view({'delete': 'delete_token'}),
        name='token_logout'
    ),
]
