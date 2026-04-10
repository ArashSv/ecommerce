import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator


class PaymentGateway(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    website_url = models.URLField(null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.slug} {'- active' if self.is_active else '- not_active'}"


# class status(models.Model) :
#     ...


class Payment(models.Model):


    class Status(models.TextChoices):
        # 1. Initial state: Record created in DB, generic info set
        INITIATED = 'INITIATED', _('Initiated')
        # 2. User has been sent to the banking gateway
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        # 3. Bank callback received, money is blocked but not yet Verified/Captured by us
        # This is CRITICAL for handling "lost" transactions (Money deducted but not verified)
        WAITING_FOR_VERIFY = 'WAITING_FOR_VERIFY', _('Waiting for Verification')
        # 4. Final Success State
        COMPLETED = 'COMPLETED', _('Completed')
        # 5. User clicked cancel or closed the bank page
        CANCELED = 'CANCELED', _('Canceled')
        # 6. Technical error, bank rejection, or verification failed
        FAILED = 'FAILED', _('Failed')
        # 7. Money fully returned to user
        FULLY_REFUNDED = 'FULLY_REFUNDED', _('Fully Refunded')
        # 8. Part of the money returned (e.g. 1 item out of 3 was returned)
        PARTIALLY_REFUNDED = 'PARTIALLY_REFUNDED', _('Partially Refunded')


    class Currency(models.TextChoices):
        IRT = 'IRT', _('Toman')
        IRR = 'IRR', _('Rial')

    # prevents sequential ID enumeration
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='payments')
    order = models.ForeignKey("orders.Order", on_delete=models.SET_NULL, null=True, related_name='payments')
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.PROTECT, related_name='payments')

    amount = models.DecimalField(max_digits=14, decimal_places=0, validators=[MinValueValidator(Decimal('1'))])
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.IRT)

    transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True, db_index=True)
    reference_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)

    status = models.CharField(max_length=30, choices=Status.choices, default=Status.CREATED, db_index=True)

    description = models.TextField(blank=True)
    failure_reason = models.TextField(blank=True)
    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"{self.transaction_id} - {self.status}"

    @property
    def is_paid(self):
        return self.status in [self.Status.COMPLETED, self.Status.PARTIALLY_REFUNDED, self.Status.FULLY_REFUNDED]


class Refund(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending Approval')
        PROCESSING = 'PROCESSING', _('Processing')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')

    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, related_name='refunds')

    amount = models.DecimalField(max_digits=14, decimal_places=0, validators=[MinValueValidator(Decimal('1'))])
    currency = models.CharField(max_length=3, default='IRT')

    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    gateway_refund_id = models.CharField(max_length=255, blank=True, null=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            total_refunded = self.payment.refunds.filter(status='COMPLETED').aggregate(total_amount=Sum("amount"))
            total_refunded_amount = total_refunded.get('total_amount', Decimal('0'))

            if total_refunded_amount + self.amount > self.payment.amount:
                raise ValueError(
                    _("Refund amount exceeds remaining payment balance. "
                      "Total refunded: %(total_refunded)s, Requested refund: %(requested_refund)s") %
                    {'total_refunded': total_refunded_amount, 'requested_refund': self.amount}
                )

        super().save(*args, **kwargs)


class PaymentLog(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, related_name='logs')
    url = models.URLField(max_length=500, blank=True, null=True)
    method = models.CharField(max_length=10, default='POST')

    request_headers = models.JSONField(default=dict, blank=True, null=True)
    request_body = models.TextField(blank=True, null=True)

    response_headers = models.JSONField(default=dict, blank=True, null=True)
    response_body = models.TextField(blank=True, null=True)
    response_status_code = models.PositiveSmallIntegerField(null=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)