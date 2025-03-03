from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView

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
    # path('auth/', include('djoser.urls')),
    # path('auth/', include('djoser.urls.jwt')),
    path(
        'api/users/',
        CustomUserViewSet.as_view({'post': 'create'}),
        name='register'
    ),
    path(
        'api/auth/token/login/',
        TokenObtainPairView.as_view(),
        name='token_login'
    ),
    # path(
    #     'api/auth/token/logout/',
    #     CustomUserViewSet.as_view({'delete': 'delete_token'}),
    #     name='token_logout'
    # ),
]
