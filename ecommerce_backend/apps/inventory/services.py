from django.utils import timezone
from django.db import transaction
from django.db.models import F
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError
from .models import StockRecord, Reservation, ReservationStatus


class ReservationService:
    def __init__(self, checkout):
        self.checkout = checkout

    def reserve(self, cart_items):
        reservation_tokens = []

        with transaction.atomic():
            for cart_item in cart_items["items"]:
                stock_data = cart_item["stockrecord"]
                quantity = cart_item["quantity"]

                stock_id = stock_data["id"]

                updated = StockRecord.objects.filter(
                    id=stock_id,
                    quantity__gte=F("reserved_quantity") + quantity
                ).update(
                    reserved_quantity=F("reserved_quantity") + quantity
                )

                if not updated:
                    product_name = (
                        stock_data
                        .get("product_variant", {})
                        .get("product", {})
                        .get("name", "Unknown product")
                    )
                    raise ValidationError(
                        _("Not enough stock for %(product)s")
                        % {"product": product_name}
                    )

                stock = StockRecord.objects.select_for_update().get(id=stock_id)

                reservation = Reservation.objects.create(
                    checkout=self.checkout,
                    stockrecord=stock,
                    quantity=quantity
                )

                reservation_tokens.append(reservation.id)

        return reservation_tokens

    def release(self, reservation_ids):
        released_tokens = []

        with transaction.atomic():
            reservations = (
                Reservation.objects.
                select_for_update()
                .select_related('stockrecord')
                .filter(id__in=reservation_ids, status=ReservationStatus.RESERVED)
            )

            if not reservations.exists():
                raise ValidationError(_("No reservations found to release."))

            for reservation in reservations:
                stock = reservation.stockrecord

                updated = StockRecord.objects.filter(
                    id=stock.id,
                    reserved_quantity__gte=reservation.quantity
                ).update(
                    reserved_quantity=F('reserved_quantity') - reservation.quantity
                )

                if not updated:
                    raise ValidationError(
                        _("Reserved quantity mismatch for %(product)s") % {
                            "product": stock.product_variant.product.name}
                    )

                Reservation.objects.filter(id=reservation.id).update(status=ReservationStatus.RELEASED, released_at=timezone.now())

                released_tokens.append(reservation.id)

            return released_tokens

    def consume(self, reservation_ids):
        consumed_tokens = []

        with transaction.atomic():
            reservations = (
                Reservation.objects
                .select_for_update()
                .select_related('stockrecord')
                .filter(id__in=reservation_ids, status=ReservationStatus.RESERVED)
                .order_by('id')
            )

            if not reservations.exists():
                raise ValidationError(_("No reservations found to consume."))

            for reservation in reservations:
                stock = reservation.stockrecord

                updated = StockRecord.objects.filter(
                    id=stock.id,
                    reserved_quantity__gte=reservation.quantity,
                ).update(
                    reserved_quantity=F('reserved_quantity') - reservation.quantity,
                    quantity=F('quantity') - reservation.quantity
                )

                if not updated:
                    raise ValidationError(
                        _("Unable to consume reservation for %(product)s. Possible stock inconsistency.") % {
                            "product": stock.product_variant.product.name
                        }
                    )

                Reservation.objects.filter(id=reservation.id).update(status=ReservationStatus.CONSUMED, consumed_at=timezone.now())

                consumed_tokens.append(reservation.id)

            return consumed_tokens