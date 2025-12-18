from django.contrib import admin
from .models import Carrier, CarrierService, Shipment

admin.site.register(Carrier)
admin.site.register(CarrierService)
admin.site.register(Shipment)
