from django.urls import include, path
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

api_urls = [path('', include(router.urls)), ]

auth_urls = [path('', include('djoser.urls.authtoken'))]

urlpatterns = [
    path('', include(api_urls)),
    path('auth/', include(auth_urls))
]
