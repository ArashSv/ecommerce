from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.shipping.models import ShippingMethod


class Checkout(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    session_id = models.CharField(max_length=128, null=True, blank=True)  # guest session for anonymous users
    cart_snapshot = models.JSONField()  #[{stockrecord_id, qty, unit_price}]
    address_snapshot = models.JSONField(null=True, blank=True)
    shipping_method = models.ForeignKey(ShippingMethod, null=True, blank=True, on_delete=models.SET_NULL)
    payment_intent_id = models.CharField(max_length=256, null=True, blank=True)
    amount = models.BigIntegerField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=15)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Checkout {self.id} for {self.user or self.session_id}"