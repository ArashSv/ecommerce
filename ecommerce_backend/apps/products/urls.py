from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.products.views.public import CategoryViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]