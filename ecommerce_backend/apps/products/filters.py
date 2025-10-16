import django_filters
from django.db.models import Min
from django_filters import rest_framework as filters
from .models import *


class ProductFilter(filters.FilterSet):
    brand = django_filters.CharFilter(field_name='brand__slug', lookup_expr='iexact')
    brand_id = django_filters.NumberFilter(field_name='brand__id', lookup_expr='exact')
    category = django_filters.CharFilter(field_name='category__slug', lookup_expr='iexact')
    category_id = django_filters.NumberFilter(field_name='category__id', lookup_expr='exact')
    available = django_filters.BooleanFilter(method='filter_available', label='Available')
    min_price = django_filters.NumberFilter(method='filter_min_price', label='Min Price')
    max_price = django_filters.NumberFilter(method='filter_max_price', label='Max Price')


    class Meta:
        model = Product
        fields = ['available',
                  'category', 'category_id',
                  'brand', 'brand_id',
                  'min_price', 'max_price']


    def filter_available(self, queryset, name, value):
        print(queryset)
        if value:
            return queryset.filter(
                variants__stockrecords__quantity__gt=F('variants__stockrecords__reserved_quantity')
            ).distinct()
        return queryset

    def filter_min_price(self, queryset, name, value):
        return queryset.annotate(
            min_price=Min('variants__stockrecords__sales_price')
        ).filter(min_price__gte=value)

    def filter_max_price(self, queryset, name, value):
        return queryset.annotate(
            min_price=Min('variants__stockrecords__sales_price')
        ).filter(min_price__lte=value)
