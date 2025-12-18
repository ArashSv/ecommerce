from django.urls import path, include


urlpatterns = [
    path('', include('apps.cart.urls')),
    path('', include('apps.inventory.urls')),
    path('', include('apps.orders.urls')),
    path('', include('apps.payments.urls')),
    path('', include('apps.products.urls')),
    path('', include('apps.users.urls')),
    path('', include('apps.shipping.urls')),
]
