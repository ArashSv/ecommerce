from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.products.views.public import CategoryViewSet, ProductViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]