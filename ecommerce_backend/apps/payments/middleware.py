import json
from django.utils.deprecation import MiddlewareMixin
from ipware import get_client_ip
from apps.payments.models import PaymentLog


class PaymentLoggingMiddleware(MiddlewareMixin):
    PAYMENT_PATHS = [
        '/api/payments/create/',
        '/api/payments/callback/',
    ]

    def process_request(self, request):
        if request.path not in self.PAYMENT_PATHS:
            return None

        payment = PaymentLog.objects.create(
            url = request.build_absolute_uri(),
            method = request.method,
            request_headers = self._get_headers(request),
            request_body = self._get_body(request),
            ip_address = self._get_client_ip(request)
        )

        request.payment_log_id = payment.pk

        return None

    def _get_headers(self, request):
        headers = {}
        for key, value in request.META.items():
            if key.startswith('HTTP_'):
                header_name = key[5:]
                headers[header_name] = value

        return headers

    def _get_body(self, request):
        if request.method in ['POST', 'PUT', 'PATCH']:
            if request.content_type == 'application/json':
                try:
                    return json.dumps(request.JSON())
                except:
                    return request.body.decode('utf-8', errors='ignore')
            return request.body.decode('utf-8', errors='ignore')
        return None

    def _get_client_ip(self, request):
        try:
            ip, is_routable = get_client_ip(request)
            return ip
        except Exception:
            return None
