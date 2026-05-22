from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.inventory.models import StockRecord
from apps.users.models import Address


class OrderStatus(models.TextChoices):
    PENDING = 'pending', _('Awaiting Registration') # Order created, awaiting payment
    PROCESSING = 'processing', _('Processing/Preparing')
    SHIPPED = 'shipped', _('Shipped')
    DELIVERED = 'delivered', _('Delivered')
    CANCELED = 'canceled', _('Canceled')
    REFUNDED = 'refunded', _('Refunded')


class Order(models.Model):
    order_number = models.CharField(max_length=64, unique=True, db_index=True, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='orders')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='orders')
    address_snapshot = models.JSONField(null=True, blank=True)
    shipping_cost = models.PositiveBigIntegerField(default=0)
    subtotal = models.PositiveBigIntegerField(default=0)
    final_total = models.PositiveBigIntegerField(default=0)
    status = models.CharField(max_length=32, choices=OrderStatus, default=OrderStatus.PENDING)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_paid = models.BooleanField(default=False)

    def update_totals(self, save=True):
        self.items_total = self.items.aggregate(
            total=models.Sum('total_price')
        )['total'] or 0

        self.final_total = (self.subtotal + self.shipping_cost)

        if save:
            self.save(update_fields=['subtotal', 'final_total'])

    def save(self, *args, **kwargs):
        # if not self.order_number:
        #     self.order_number = generate_order_number()
        address = self.address
        if address and not self.address_snapshot:
            self.address_snapshot = {
                "full_name": f"{address.first_name} {address.last_name}",
                "mobile_number": address.mobile_number,
                "email": address.email,

                "province":address.province,
                "city":address.city,
                "postal_address":address.postal_address,
                "plaque": address.plaque,
                "postal_code":address.postal_code,

                "unit": address.unit if address.unit else None,
                "latitude": address.latitude if address.latitude else None,
                "longitude": address.longitude if address.longitude else None,
            }

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} - {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    stockrecord = models.ForeignKey(StockRecord, on_delete=models.SET_NULL, null=True)
    stockrecord_snapshot = models.JSONField(null=True, blank=True)
    quantity = models.PositiveSmallIntegerField(default=1)
    unit_price = models.PositiveBigIntegerField(default=0)
    total_price = models.PositiveBigIntegerField(default=0)

    class Meta:
        unique_together = (('order','stockrecord'),)

    def save(self, *args, **kwargs):
        stockrecord = self.stockrecord

        if not self.pk and not self.unit_price and stockrecord:
            self.unit_price = stockrecord.sales_price
        self.total_price = self.unit_price * self.quantity

        if stockrecord and not self.stockrecord_snapshot:
            product = stockrecord.product_variant.product
            self.stockrecord_snapshot = {
                "title": product.name,
                "sku": stockrecord.product_variant.sku,
                "slug": product.slug,
                "main_image": product.main_image.url if product.main_image else "",
                "price": str(stockrecord.sales_price),
                "weight": stockrecord.product_variant.weight,
                "length": stockrecord.product_variant.length,
                "width": stockrecord.product_variant.width,
                "height": stockrecord.product_variant.height,
            }

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Item {self.id} ({self.quantity} x {self.unit_price})"

