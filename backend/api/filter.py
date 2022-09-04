from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from api.models import Recipes, Tags


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class FilterRecipe(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tags.objects.all(),
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipes
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorite_recipe__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(favorite_r_user__user=self.request.user)
        return queryset

