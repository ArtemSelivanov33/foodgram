from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import (
    IngredientViewSet, RecipeViewSet, TagViewset, UserListViewSet
)

app_name = 'api'

router_v1 = SimpleRouter()

router_v1.register('tags', TagViewset)
router_v1.register('ingredients', IngredientViewSet)
router_v1.register('recipes', RecipeViewSet)
router_v1.register('users', UserListViewSet)


urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
