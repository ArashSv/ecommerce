from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.products.views.public import CategoryViewSet, ProductViewSet, ProductBrandViewSet


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'brands', ProductBrandViewSet, basename='brand')

urlpatterns = [
    path('', include(router.urls)),
]