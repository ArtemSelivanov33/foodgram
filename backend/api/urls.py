from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

api_router = DefaultRouter()

api_router.register(
    'users',
    views.UsersViewSet,
    basename='users'
)

api_router.register(
    'tags',
    views.TagsViewSet,
    basename='tags'
)

api_router.register(
    'ingredients',
    views.IngredientsViewSet,
    basename='ingredients'
)

api_router.register(
    'recipes',
    views.RecipeViewSet,
    basename='recipes'
)

urlpatterns = [
    path('', include(api_router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
