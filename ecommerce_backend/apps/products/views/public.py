from django_filters.rest_framework import DjangoFilterBackend
from taggit.models import Tag
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.products.models import Product, Category, ProductBrand
from apps.products.serializers.public import (ProductDetailSerializer, ProductListSerializer, CategoryTreeSerializer, CategoryNodeSerializer,
                                              ProductBrandSerializer, TagSerializer)
from apps.products.filters import ProductFilter


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'slug'

    queryset = Product.objects.all()

    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ('name', 'description', 'tags__name', 'brand__name', 'product_type__name')
    ordering_fields = ('created_at',)

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'slug'

    def get_queryset(self):
        if self.action == 'list':
            return Category.objects.filter(depth=1)
        else:
            return Category.objects.all()

    def get_serializer_class(self):
        match self.action:
            case 'list':
                return CategoryTreeSerializer
            case 'retrieve':
                return CategoryNodeSerializer
        return None

    @action(detail=True, methods=['get'], url_path='products')
    def products(self, request, slug=None):
        category = self.get_object()
        products = Product.objects.filter(category=category)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductBrandViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'slug'

    queryset = ProductBrand.objects.all()
    serializer_class = ProductBrandSerializer

    @action(detail=True, methods=['get'], url_path='products')
    def products(self, request, slug=None):
        brand = self.get_object()
        products = Product.objects.filter(brand=brand)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductTagViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'slug'

    queryset = Tag.objects.filter(taggit_taggeditem_items__content_type__model='product').distinct()
    serializer_class = TagSerializer

    @action(detail=True, methods=['get'], url_path='products')
    def products(self, request, slug=None):
        tag = self.get_object()
        products = Product.objects.filter(tags__slug=tag)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)