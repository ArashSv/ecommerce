from rest_framework import viewsets
from apps.products.models import Product, Category
from apps.products.serializers.public import ProductSerializer, CategoryTreeSerializer, CategoryNodeSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


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