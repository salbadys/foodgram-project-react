from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipesViewSet, TagsViewSet, IngredientViewSet, \
    FavoriteViewSet, FollowListView, FollowViewSet, \
    DownloadListView, AddCartViewSet, CreateUserView

app_name = 'api'

router = DefaultRouter()

router.register('recipes', RecipesViewSet)
router.register('tags', TagsViewSet)
router.register('ingredients', IngredientViewSet)
router.register('users', CreateUserView, basename='users')

urlpatterns = [
    path('users/subscriptions/', FollowListView.as_view()),
    path('recipes/download_shopping_cart/', DownloadListView.as_view()),
    path('', include(router.urls)),
    path('recipes/<int:recipes_id>/shopping_cart/', AddCartViewSet.as_view(),
         name='shopping_cart'),
    path('users/<int:user_id>/subscribe/', FollowViewSet.as_view(),
         name='subscribe'),
    path('recipes/<int:recipes_id>/favorite/', FavoriteViewSet.as_view(),
         name='favorite'),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
