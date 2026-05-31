from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.orders.models import Order


class ShippingMethod(models.Model):
    carrier_name = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    slug = models.SlugField(allow_unicode=True)
    delivery_min = models.PositiveSmallIntegerField(null=True, blank=True)
    delivery_max = models.PositiveSmallIntegerField(null=True, blank=True)
    base_price = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    config = models.JSONField(null=True, blank=True)
    website_url = models.URLField(null=True, blank=True)

    def __str__(self):
        status = "active" if self.is_active else "not active"
        return f"{self.slug} - status : {status}"


class ShipmentStatus(models.TextChoices):
    PENDING = 'pending', _('Awaiting Pickup')
    PICKED = 'picked', _('Picked Up')
    IN_TRANSIT = 'in_transit', _('In Transit')
    DELIVERED = 'delivered', _('Delivered')
    RETURNED = 'returned', _('Returned')
    CANCELLED = 'cancelled', _('Canceled')


class Shipment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="shipments")
    service = models.ForeignKey(ShippingMethod, on_delete=models.CASCADE, related_name="shipments")

    # Physical result data
    total_weight = models.PositiveIntegerField(help_text=_("Total actual weight in grams"))
    volumetric_weight = models.PositiveIntegerField(help_text=_("Volumetric weight in grams"))
    chargeable_weight = models.PositiveIntegerField(help_text=_("Weight used for cost calculation"))
    package_length = models.PositiveIntegerField(help_text=_("Package length in millimeters"))
    package_width = models.PositiveIntegerField(help_text=_("Package width in millimeters"))
    package_height = models.PositiveIntegerField(help_text=_("Package height in millimeters"))

    shipping_cost = models.PositiveBigIntegerField(default=0)
    tracking_number = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    label_url = models.URLField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=ShipmentStatus, default=ShipmentStatus.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['order', 'status']),
        ]


    def __str__(self):
        return f"Shipment #{self.id} for Order #{self.order_id} ({self.status})"

    def mark_picked(self):
        if self.status != ShipmentStatus.PENDING:
            raise ValueError(_("Only pending shipments can be picked."))
        self.status = ShipmentStatus.PICKED

    def mark_in_transit(self):
        if self.status not in [ShipmentStatus.PENDING, ShipmentStatus.PICKED]:
            raise ValueError(_("Only pending or picked shipments can be set as in transit."))
        self.status = ShipmentStatus.IN_TRANSIT
        self.shipped_at = timezone.now()

    def mark_delivered(self):
        if self.status != ShipmentStatus.IN_TRANSIT:
            raise ValueError(_("Only in transit shipments can be delivered."))
        self.status = ShipmentStatus.DELIVERED
        self.delivered_at = timezone.now()

    def mark_returned(self):
        if self.status not in [ShipmentStatus.IN_TRANSIT, ShipmentStatus.DELIVERED]:
            raise ValueError(_("Only in transit or delivered shipments can be returned."))
        self.status = ShipmentStatus.RETURNED

    def mark_cancelled(self):
        if self.status not in [ShipmentStatus.PENDING, ShipmentStatus.PICKED]:
            raise ValueError(_("Only pending or picked shipments can be cancelled."))
        self.status = ShipmentStatus.CANCELLED


class TrackingEvent(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='events')
    event_code = models.CharField(max_length=64)  # e.g. 'PICKED', 'IN_TRANSIT'
    message = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    raw_payload = models.JSONField(null=True, blank=True)