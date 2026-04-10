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
        CREATED = 'CREATED', _('Created')
        PROCESSING = 'PROCESSING', _('Processing')
        SUCCESS = 'SUCCESS', _('Success')
        FAILED = 'FAILED', _('Failed')


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
        return self.status in [self.Status.SUCCESS]

    def mark_created(self):
        if self.status in [self.Status.PROCESSING, self.Status.SUCCESS, self.Status.FAILED]:
            raise ValueError("Invalid transition")
        self.status = self.Status.CREATED

    def mark_processing(self):
        if self.status != self.Status.CREATED:
            raise ValueError("Invalid transition")
        self.status = self.Status.PROCESSING

    def mark_success(self, reference_id):
        if self.status not in [self.Status.CREATED, self.Status.PROCESSING]:
            raise ValueError("Invalid transition")
        self.status = self.Status.SUCCESS
        self.reference_id = reference_id

    def mark_failed(self):
        if self.status == self.Status.SUCCESS:
            raise ValueError("Invalid transition")
        self.status = self.Status.FAILED


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