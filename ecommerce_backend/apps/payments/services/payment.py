from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from apps.payments.models import PaymentGateway, Payment
from django.utils.translation import gettext as _


class PaymentService:
    def __init__(self, gateway_slug: str):
        self.gateway_slug = gateway_slug
        self.gateway = None
        self.gw = None

    def _setup(self):
        self.gw = PaymentGateway.objects.get(slug=self.gateway_slug, is_active=True)
        gateway_cls = self._load_gateway_class(self.gw.slug)
        self.gateway = gateway_cls(config=self.gw.config)

    def _load_gateway_class(self, slug: str):
        mapping = {
            "aqaepardakht": "apps.payments.services.gateways.aqayepardakht.AqaepardakhtGateway",
        }
        cls_path = mapping[slug]
        module_name, cls_name = cls_path.rsplit(".", 1)
        module = __import__(module_name, fromlist=[cls_name])
        return getattr(module, cls_name)

    def create(self, order_id, amount, user=None, **kwargs):
        self._setup()
        create_result = self.gateway.create(amount)
        transaction_id = create_result.get('transaction_id')
        is_success = create_result.get('is_success')

        payment = Payment.objects.create(
            transaction_id=transaction_id,
            order_id=order_id,
            gateway=self.gw,
            amount=amount,
        )

        if is_success and transaction_id:
            payment.mark_created()

            payment.save(update_fields=['status', 'transaction_id'])
            startpay_url = self.gateway.get_startpay_url(transaction_id)

            response = {
                "is_success": True,
                "startpay_url": f"{startpay_url}"
            }
            return Response(response, status=status.HTTP_200_OK)

        payment.mark_failed()

        payment.save(update_fields=['status'])

        response = {
            "is_success": False,
            "code": create_result.get("code"),
            "message": create_result.get("message")
        }

        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def callback(self, request):
        self._setup()
        callback_request = self.gateway.callback(request)
        transaction_id = callback_request.get('transaction_id')
        reference_id = callback_request.get('reference_id')
        is_success = callback_request.get('is_success')

        if not transaction_id or not is_success:
            response = {
                "is_success": False,
                "message": _("Transaction failed"),
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            payment = Payment.objects.select_for_update().get(
                transaction_id=transaction_id,
                gateway=self.gw
            )

            payment.mark_processing()

            if not payment.reference_id and reference_id:
                payment.reference_id = reference_id
                payment.save(update_fields=['reference_id'])

            result = self.verify(transaction_id=transaction_id, amount=payment.amount)
            return result

    def verify(self, transaction_id, amount):
        self._setup()

        # fast check
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
            if payment.status == Payment.Status.SUCCESS:
                response = {
                    "is_success": False,
                    "message": _("The transaction has already been confirmed"),
                    "payment_id": payment.id
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Payment.DoesNotExist:
            response = {
                "is_success": False,
                "message": _("Transaction not found"),
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        verify_result = self.gateway.verify(transaction_id, amount)
        is_success = verify_result.get('is_success')
        reference_id = verify_result.get('reference_id')

        with transaction.atomic():
            payment = Payment.objects.select_for_update().get(
                transaction_id=transaction_id,
                gateway=self.gw
            )

            if payment.status == Payment.Status.SUCCESS:
                response = {
                    "is_success": False,
                    "message": _("The transaction has already been confirmed"),
                    "payment_id": payment.id
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            if not is_success:
                payment.mark_failed()
                payment.save(update_fields=['status'])
                response = {
                    "is_success": False,
                    "message": _("Transaction failed"),
                    "payment_id": payment.id
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            if not payment.reference_id and not reference_id:
                payment.mark_failed()
                payment.save(update_fields=['status'])
                response = {
                    "is_success": False,
                    "message": _("Tracking code not received from the payment gateway"),
                    "payment_id": payment.id
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            payment.mark_success(reference_id)
            payment.save(update_fields=['status', 'reference_id'])
            response = {
                "is_success": True,
                "message": _("The transaction was successful"),
                "payment_id": payment.id,
                "gateway_reference": payment.reference_id
            }
            return Response(response, status=status.HTTP_200_OK)