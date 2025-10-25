from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.products.views.public import CategoryViewSet, ProductViewSet, ProductBrandViewSet, ProductTagViewSet


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'brands', ProductBrandViewSet, basename='brand')
router.register(r'product-tags', ProductTagViewSet, basename='product_tag')

urlpatterns = [
    path('', include(router.urls)),
]