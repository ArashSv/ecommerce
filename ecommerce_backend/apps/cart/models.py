from django.db import models
from django.conf import settings
from apps.inventory.models import StockRecord
from django.db.models import Sum, F


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')

    @property
    def total_items(self):
        result = self.items.aggregate(total=Sum('quantity'))
        return result['total'] or 0

    @property
    def total_price(self):
        return self.items.aggregate(total=Sum(F('stockrecord__sales_price') * F('quantity')))['total'] or 0

    def __str__(self):
        return self.user.mobile_number


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    stockrecord = models.ForeignKey(StockRecord, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField(default=1)

    @property
    def unit_price(self):
        return self.stockrecord.sales_price

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.cart.user} : {self.stockrecord} x{self.quantity}"

    class Meta:
        unique_together = ('cart', 'stockrecord')
