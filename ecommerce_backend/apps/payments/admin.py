from django.contrib import admin
from .models import PaymentGateway, Payment, PaymentLog

admin.site.register(PaymentGateway)
admin.site.register(Payment)
admin.site.register(PaymentLog)
