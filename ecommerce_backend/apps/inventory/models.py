import uuid

from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Warehouse(BaseModel):
    name = models.CharField(max_length=64)

    province = models.CharField(max_length=64, null=True, blank=True)
    city = models.CharField(max_length=64, null=True, blank=True)

    postal_address = models.TextField(null=True, blank=True)
    postal_code = models.IntegerField(null=True, blank=True)
    plaque = models.IntegerField(null=True, blank=True)
    unit = models.CharField(max_length=4, null=True, blank=True)  # exam : 30B, 2A, ..

    # Geolocation coordinates of the address
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    def __str__(self):
        return self.name


class StockRecord(BaseModel):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stockrecords')
    product_variant = models.ForeignKey('products.ProductVariant', on_delete=models.CASCADE, related_name='stockrecords')
    quantity = models.PositiveIntegerField()
    reserved_quantity = models.PositiveIntegerField()
    reorder_threshold = models.PositiveIntegerField(null=True, blank=True)
    buy_price = models.PositiveBigIntegerField(null=True, blank=True)
    sales_price = models.PositiveBigIntegerField()

    @property
    def available_quantity(self):
        return max(self.quantity - self.reserved_quantity, 0)

    @property
    def is_available(self):
        return self.available_quantity > 0

    def __str__(self):
        return f"{self.warehouse} : {self.product_variant}({self.available_quantity})"


    class Meta:
        unique_together = (('warehouse', 'product_variant'),)


class ReservationStatus(models.TextChoices):
    RESERVED = "reserved", _("Reserved")
    RELEASED = "released", _("Released")
    CONSUMED = "consumed", _("Consumed")


class Reservation(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    checkout = models.ForeignKey('checkout.Checkout', on_delete=models.CASCADE, related_name='reservations')
    stockrecord = models.ForeignKey(StockRecord, on_delete=models.PROTECT, related_name='reservations')
    quantity = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(max_length=20, choices=ReservationStatus, default=ReservationStatus.RESERVED, db_index=True)
    released_at = models.DateTimeField(null=True, blank=True)
    consumed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.checkout} : {self.stockrecord} x{self.quantity} ({self.status})"


    class Meta:
        indexes = [
            models.Index(fields=["status"], condition=Q(status="RESERVED"), name='reservation_reserved')
        ]
        unique_together = (('checkout', 'stockrecord'),)