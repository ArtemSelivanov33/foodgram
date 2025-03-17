from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api import views

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
    basename='recipe'
)

auth_urls = [
    path(
        'token/login/',
        views.TokenCreateView.as_view(),
        name='login'
    ),
    path(
        'token/logout/',
        views.TokenDeleteView.as_view(),
        name='logout'
    )
]

urlpatterns = [
    path('auth/', include(auth_urls)),
    path('', include(api_router.urls)),
]
