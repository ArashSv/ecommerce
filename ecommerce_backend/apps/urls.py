from django.urls import path, include


urlpatterns = [
    path('cart/', include('apps.cart.urls')),
    path('inventory/', include('apps.inventory.urls')),
    path('orders/', include('apps.orders.urls')),
    path('payments/', include('apps.payments.urls')),
    path('products/', include('apps.products.urls')),
    path('users/', include('apps.users.urls'))
]
