from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from users.models import User


class Ingredient(models.Model):
    """Модель ингредиентов"""
    name = models.CharField('Имя ингредиента', max_length=20, unique=True)
    measurement_unit = models.CharField('Ед.измерения', max_length=10)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Tags(models.Model):
    """Модель тегов"""
    name = models.CharField(verbose_name='Имя тега', unique=True,
                            max_length=20)
    color = ColorField(default='#FF0000')
    slug = models.SlugField(verbose_name='Слаг тега', unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Recipes(models.Model):
    """Модель рецептов"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    name = models.CharField('Имя рецепта', max_length=200)
    image = models.ImageField(
        'Картинка',
        upload_to='image/'
    )
    text = models.TextField('Описание рецепта')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientForRecipe',
                                         related_name='recipes')
    tags = models.ManyToManyField(Tags,
                                  related_name='recipes')
    cooking_time = models.IntegerField(
        validators=[
            MaxValueValidator(200),
            MinValueValidator(1)
        ]
    )

    pub_date = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class IngredientForRecipe(models.Model):
    """Модель ингредиентов для рецептов"""
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Рецепт",
    )
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name="ingredient_for_recipe",
        verbose_name="Ингредиент в рецепте",
    )
    amount = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты для рецептов"
        constraints = (
            models.UniqueConstraint(
                fields=('ingredients', 'recipe',),
                name='unique recipe',
            ),
        )


class FavoriteUser(models.Model):
    """Рецепт в избранном"""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="favorite",
                             verbose_name="Пользователь")
    recipes = models.ForeignKey(Recipes,
                                on_delete=models.CASCADE,
                                related_name="favorite_recipe",
                                verbose_name="Рецепт")

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = "Избранное пользователей"
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipes'],
                                    name='unique')
        ]


class ShopCart(models.Model):
    """Корзина пользователя"""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="user",
                             verbose_name="Пользователь")
    recipes = models.ForeignKey(Recipes,
                                on_delete=models.CASCADE,
                                related_name="favorite_r_user",
                                verbose_name="Рецепт")

    class Meta:
        verbose_name = "Покупка"
        verbose_name_plural = "Корзина покупок"
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipes'],
                                    name='unique ShopCart')
        ]
