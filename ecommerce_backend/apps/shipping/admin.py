from django.contrib import admin
from .models import Shipment, ShippingMethod

admin.site.register(Shipment)
admin.site.register(ShippingMethod)
