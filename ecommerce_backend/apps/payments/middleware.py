from django.utils.deprecation import MiddlewareMixin


class PaymentLoggingMiddleware(MiddlewareMixin):
    PAYMENT_PATHS = [
        '/api/payments/create/',
        '/api/payments/callback/',
        '/api/payments/verify/',
    ]

    def process_request(self, request):
        ...

    def process_response(self, request, response):
        ...
