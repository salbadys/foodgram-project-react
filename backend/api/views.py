from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import viewsets, filters, status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, \
    AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from .filter import FilterRecipe
from .models import Recipes, Tags, Ingredient, FavoriteUser, ShopCart, \
    IngredientForRecipe
from users.models import User, Follow
from .serializers import RecipesSerializer, TagsSerializer, \
    IngredientSerializer, FavoriteSerializer, \
    FollowUserSerializer, ShoppingSerializer, RegistrationSerializer, \
    RecipeSerializerPost


class CreateUserView(UserViewSet):
    """Просмотр пользователей"""
    serializer_class = RegistrationSerializer

    def get_queryset(self):
        return User.objects.all()


class FollowViewSet(APIView):
    """Удаление и добавление подписки на пользователя"""
    serializer_class = FollowUserSerializer

    def post(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        if user_id == request.user.id:
            return Response(
                {'error': 'Нельзя подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Follow.objects.filter(
                user=request.user,
                author_id=user_id
        ).exists():
            return Response(
                {'error': 'Вы уже подписаны на пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        author = get_object_or_404(User, id=user_id)
        Follow.objects.create(
            user=request.user,
            author_id=user_id
        )
        return Response(
            self.serializer_class(author, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        get_object_or_404(User, id=user_id)
        subscription = Follow.objects.filter(
            user=request.user,
            author_id=user_id
        )
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Вы не подписаны на пользователя'},
            status=status.HTTP_400_BAD_REQUEST
        )


class FollowListView(ListAPIView):
    """Просмотр подписок"""
    serializer_class = FollowUserSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class DownloadListView(APIView):
    """Загрузка списка покупок"""
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        user = request.user
        shopping_cart = user.user.all()
        buy_list = {}
        shop_list = []
        for record in shopping_cart:
            recipe = record.recipes
            ingredients = IngredientForRecipe.objects.filter(recipe=recipe)
            for ingredient in ingredients:
                amount = ingredient.amount
                name = ingredient.ingredients.name
                measurement_unit = ingredient.ingredients.measurement_unit
                if name not in buy_list:
                    buy_list[name] = {
                        'measurement_unit': measurement_unit,
                        'amount': amount
                    }
                else:
                    buy_list[name]['amount'] = (buy_list[name]['amount']
                                                   + amount)
        shop_list.append('Список ваших покупок: ')
        for item in buy_list:
            shop_list.append(f'{item} - {buy_list[item]["amount"]} '
                                f'{buy_list[item]["measurement_unit"]};')
        shop_list.append(' ')
        shop_list.append('- Ваш сервис рецептов Foodgram')
        response = HttpResponse(shop_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="BuyList.txt"'
        return response


class AddCartViewSet(APIView):
    """Добавить и удалить из покупки"""

    def post(self, request, recipes_id):
        user = request.user
        data = {
            'recipes': recipes_id,
            'user': user.id
        }
        serializer = ShoppingSerializer(data=data,
                                        context={'request': request})
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipes_id):
        user = request.user
        recipes = get_object_or_404(Recipes, id=recipes_id)
        ShopCart.objects.filter(user=user, recipes=recipes).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(APIView):
    """Добавить в избранное"""

    def post(self, request, recipes_id):
        user = request.user
        data = {
            'recipes': recipes_id,
            'user': user.id
        }
        serializer = FavoriteSerializer(data=data,
                                        context={'request': request})
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipes_id):
        user = request.user
        recipes = get_object_or_404(Recipes, id=recipes_id)
        FavoriteUser.objects.filter(user=user, recipes=recipes).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Просмотр ингридиентов"""
    permission_classes = (AllowAny,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    pagination_class = None
    search_fields = ['^name', ]


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр тегов"""
    pagination_class = None
    permission_class = None
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    """Просмотр и работы с рецептами"""
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = FilterRecipe
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Recipes.objects.all()

    def get_serializer_class(self):
        print(self.request.method)
        if self.request.method == 'GET':
            return RecipesSerializer
        return RecipeSerializerPost
