from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.validators import UniqueTogetherValidator
from users.models import User, Follow
from .models import Recipes, Tags, Ingredient, FavoriteUser, ShopCart, \
    IngredientForRecipe
from rest_framework import serializers


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Краткая информация о рецепте"""

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowUserSerializer(UserSerializer):
    """Подписка на пользователя"""

    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'recipes',
            'recipes_count')

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(recipes, many=True).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Избранное пользователя"""

    class Meta:
        fields = ('user', 'recipes')
        model = FavoriteUser
        validators = [
            UniqueTogetherValidator(
                queryset=FavoriteUser.objects.all(),
                fields=('user', 'recipes'),
                message='Рецепт уже добавлен в избранное'
            )
        ]

    def to_representation(self, instance):
        requset = self.context.get('request')
        return ShortRecipeSerializer(
            instance.recipes,
            context={'request': requset}
        ).data


class ShoppingSerializer(serializers.ModelSerializer):
    """Покупки пользователя"""

    class Meta:
        fields = ('user', 'recipes')
        model = ShopCart
        validators = [
            UniqueTogetherValidator(
                queryset=FavoriteUser.objects.all(),
                fields=('user', 'recipes'),
                message='Рецепт уже добавлен в покупки'
            )
        ]

    def to_representation(self, instance):
        requset = self.context.get('request')
        return ShortRecipeSerializer(
            instance.recipes,
            context={'request': requset}
        ).data


class IngredientSerializer(serializers.ModelSerializer):
    """Ингридиенты"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', "measurement_unit")


class TagsSerializer(serializers.ModelSerializer):
    """Теги"""

    class Meta:
        model = Tags
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )
        read_only_fields = '__all__',


class RegistrationSerializer(UserCreateSerializer):
    """Регистрация пользователя"""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed', 'password')
        write_only_fields = ('password',)
        read_only_fields = ('id',)
        extra_kwargs = {'is_subscribed': {'required': False}}

    def to_representation(self, obj):
        result = super(RegistrationSerializer, self).to_representation(obj)
        result.pop('password', None)
        return result


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Ингридиент и количество"""
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'name', "measurement_unit", "amount")


class RecipesSerializer(serializers.ModelSerializer):
    """Рецепты"""
    ingredients = serializers.SerializerMethodField(read_only=True)
    tags = TagsSerializer(many=True)
    author = RegistrationSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    def get_ingredients(self, obj):
        queryset = IngredientForRecipe.objects.filter(recipe=obj)
        return IngredientAmountSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return FavoriteUser.objects.filter(user=request.user,
                                           recipes=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShopCart.objects.filter(
            user=request.user, recipes=obj).exists()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )


class IngredientAmountRecipeSerializer(serializers.ModelSerializer):
    """Количество ингредиента"""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'amount')


class CustomUserSerializer(UserSerializer):
    """Просмотр подписки"""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()


class RecipeSerializerPost(serializers.ModelSerializer):
    """Создание рецепта"""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(), many=True)
    ingredients = IngredientAmountRecipeSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipes
        fields = (
            'id', 'author', 'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time')

    def validate(self, data):
        ingredients = data['ingredients']
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError({
                    'ingredients': 'Ингредиентам нельзя повторяться!'
                })
            ingredients_list.append(ingredient_id)
            amount = ingredient['amount']
            if int(amount) <= 0:
                raise serializers.ValidationError({
                    'amount': 'В рецепте должен быть ингредиент!'
                })

        tags = data['tags']
        if not tags:
            raise serializers.ValidationError({
                'tags': 'Выберите минимум один тег!'
            })
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError({
                    'tags': 'Теги - уникальны!'
                })
            tags_list.append(tag)

        cooking_time = data['cooking_time']
        if int(cooking_time) <= 0:
            raise serializers.ValidationError({
                'cooking_time': 'Время не может быть меньше 1 минуты!'
            })
        return data

    @staticmethod
    def create_ingredients(ingredients, recipes):
        for ingredient in ingredients:
            IngredientForRecipe.objects.create(
                recipe=recipes, ingredients=ingredient['id'],
                amount=ingredient['amount']
            )

    @staticmethod
    def create_tags(tags, recipes):
        for tag in tags:
            recipes.tags.add(tag)

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipes.objects.create(author=author, **validated_data)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipesSerializer(instance, context=context).data

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientForRecipe.objects.filter(recipe=instance).delete()
        self.create_tags(validated_data.pop('tags'), instance)
        self.create_ingredients(validated_data.pop('ingredients'), instance)
        return super().update(instance, validated_data)
