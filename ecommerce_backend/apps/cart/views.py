from functools import wraps
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from apps.cart.serializers.session import CartSessionSerializer
from apps.cart.serializers.actions import AddItemInputSerializer, UpdateQuantityInputSerializer, RemoveItemInputSerializer
from apps.cart.serializers.user import CartUserSerializer
from apps.cart.services import CartService


def handle_service_errors(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        try:
            return func(self, request, *args, **kwargs)
        except DjangoValidationError as exc:
            raise DRFValidationError(detail=str(exc))
    return wrapper


class CartViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    def _get_service(self, request):
        return CartService(user=request.user if getattr(request, "user", None) and request.user.is_authenticated else None,
                           session=getattr(request, "session", None))

    def list(self, request):
        svc = self._get_service(request)
        if request.user and request.user.is_authenticated:
            cart_obj = svc.get_cart_object()
            serializer = CartUserSerializer(cart_obj, context={"request": request})
            data = serializer.data
        else:
            items = svc.get_session_items()
            totals = svc.get_totals()
            serializer = CartSessionSerializer({
                "items": items,
                "total_items": totals["total_items"],
                "total_price": totals["total_price"],
            }, context={"request": request})
            data = serializer.data
        return Response(data)

    @handle_service_errors
    @action(detail=False, methods=["post"])
    def add_item(self, request):
        serializer = AddItemInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        svc = self._get_service(request)
        svc.add_item(stockrecord_id=serializer.validated_data["stockrecord_id"],
                     quantity=serializer.validated_data.get("quantity", 1))
        return self.list(request)

    @handle_service_errors
    @action(detail=False, methods=["patch"])
    def update_quantity(self, request):
        serializer = UpdateQuantityInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        svc = self._get_service(request)
        svc.update_quantity(stockrecord_id=serializer.validated_data["stockrecord_id"],
                            quantity=serializer.validated_data["quantity"])
        return self.list(request)

    @handle_service_errors
    @action(detail=False, methods=["delete"])
    def remove_item(self, request):
        serializer = RemoveItemInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        svc = self._get_service(request)
        svc.remove_item(stockrecord_id=serializer.validated_data["stockrecord_id"])
        return self.list(request)

    @handle_service_errors
    @action(detail=False, methods=["post"])
    def clear(self, request):
        svc = self._get_service(request)
        svc.clear_cart()
        return self.list(request)
