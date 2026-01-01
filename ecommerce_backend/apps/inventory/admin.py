from django.contrib import admin
from .models import Warehouse, StockRecord, Reservation

admin.site.register(Warehouse)
admin.site.register(StockRecord)
admin.site.register(Reservation)
