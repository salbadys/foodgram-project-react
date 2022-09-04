from django.contrib import admin

from api.models import Recipes, Tags, Ingredient, FavoriteUser, ShopCart, \
    IngredientForRecipe


class FavoriteUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipes')


class RecipesAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name')
    search_fields = ('author', 'name', 'tags')
    list_filter = ('author', 'name', 'tags')
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class ShopCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipes')
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'


class IngredientForRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredients', 'amount')
    empty_value_display = '-пусто-'


admin.site.register(Recipes, RecipesAdmin)
admin.site.register(Tags, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(FavoriteUser, FavoriteUserAdmin)
admin.site.register(ShopCart, ShopCartAdmin)
admin.site.register(IngredientForRecipe, IngredientForRecipeAdmin)
