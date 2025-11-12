"""
- get_session_items() -> list of dicts with keys: 'stockrecord', 'quantity', 'unit_price', 'total_price'
- get_totals() -> dict with keys: 'total_items', 'total_price'
- get_cart_object() -> Cart instance (or None)
"""

from typing import Optional, Dict, List
from django.db import transaction
from django.db.models import F
from django.core.exceptions import ValidationError as DjangoValidationError
from apps.cart.models import Cart, CartItem
from apps.inventory.models import StockRecord


class CartService:
    SESSION_KEY = "cart"

    def __init__(self, user=None, session=None):
        self.user = user if getattr(user, "is_authenticated", False) else None
        self.session = session
        if self.session is not None:
            # ensure session structure exists
            self.session.setdefault(self.SESSION_KEY, {"items": {}})
            self.session_cart = self.session[self.SESSION_KEY]["items"]
        else:
            self.session_cart = {}

    # ---------------- session helpers ----------------
    def _save_session(self):
        if self.session is not None:
            self.session[self.SESSION_KEY] = {"items": self.session_cart}
            # Mark modified if session object has attribute
            if hasattr(self.session, "modified"):
                self.session.modified = True

    # ---------------- cart object (user) ----------------
    def get_cart_object(self) -> Optional[Cart]:
        if not self.user:
            return None
        if not hasattr(self, "_cart"):
            self._cart, _ = Cart.objects.get_or_create(user=self.user)
        return self._cart

    # ---------------- session items DTO ----------------
    def get_session_items(self) -> List[Dict]:
        if not self.session_cart:
            return []
        try:
            stock_ids = [int(k) for k in self.session_cart.keys()]
        except ValueError:
            return []

        stocks = (
            StockRecord.objects
            .select_related("product_variant__product")
            .filter(id__in=stock_ids)
        )
        stock_map = {s.id: s for s in stocks}

        items = []
        for sid_str, data in self.session_cart.items():
            try:
                sid = int(sid_str)
            except ValueError:
                continue
            stock = stock_map.get(sid)
            if not stock:
                continue
            qty = int(data.get("quantity", 0))
            unit_price = stock.sales_price or 0
            items.append({
                "stockrecord": stock,
                "quantity": qty,
                "unit_price": unit_price,
                "total_price": qty * unit_price,
            })
        return items

    # ---------------- totals ----------------
    def get_totals(self) -> Dict[str, int]:
        if self.user:
            cart = self.get_cart_object()
            return {"total_items": cart.total_items, "total_price": cart.total_price}

        items = self.get_session_items()
        total_items = sum(item["quantity"] for item in items)
        total_price = sum(item["total_price"] for item in items)
        return {"total_items": total_items, "total_price": total_price}

    # ---------------- add item ----------------
    @transaction.atomic
    def add_item(self, stockrecord_id: int, quantity: int = 1) -> None:
        if quantity <= 0:
            raise DjangoValidationError("تعداد باید بزرگ‌تر از صفر باشد.")

        try:
            stock = StockRecord.objects.select_for_update().get(id=stockrecord_id)
        except StockRecord.DoesNotExist:
            raise DjangoValidationError("محصول یافت نشد.")

        available = getattr(stock, "available_quantity", getattr(stock, "quantity", 0))
        if self.user:
            cart = self.get_cart_object()
            # Try to lock and get existing CartItem
            try:
                item = (
                    CartItem.objects.select_for_update().get(cart=cart, stockrecord=stock)
                )
                new_total = item.quantity + quantity
                if new_total > available:
                    raise DjangoValidationError("تعداد بیشتر از موجودی محصول است.")
                item.quantity = F("quantity") + quantity
                item.save(update_fields=["quantity"])
            except CartItem.DoesNotExist:
                if quantity > available:
                    raise DjangoValidationError("تعداد بیشتر از موجودی محصول است.")
                CartItem.objects.create(cart=cart, stockrecord=stock, quantity=quantity)
            return

        # session (guest)
        sid = str(stockrecord_id)
        current_qty = int(self.session_cart.get(sid, {}).get("quantity", 0))
        if current_qty + quantity > available:
            raise DjangoValidationError("تعداد بیشتر از موجودی محصول است.")
        self.session_cart[sid] = {"quantity": current_qty + quantity}
        self._save_session()

    # ---------------- update quantity ----------------
    @transaction.atomic
    def update_quantity(self, stockrecord_id: int, quantity: int) -> None:
        if quantity <= 0:
            return self.remove_item(stockrecord_id)

        try:
            stock = StockRecord.objects.select_for_update().get(id=stockrecord_id)
        except StockRecord.DoesNotExist:
            raise DjangoValidationError("کالای مورد نظر وجود ندارد.")

        max_available = getattr(stock, "available_quantity", getattr(stock, "quantity", 0))
        if quantity > max_available:
            raise DjangoValidationError("موجودی کافی نیست.")

        if self.user:
            cart = self.get_cart_object()
            item = CartItem.objects.filter(cart=cart, stockrecord_id=stockrecord_id).first()
            if not item:
                raise DjangoValidationError("این کالا در سبد شما نیست.")
            item.quantity = quantity
            item.save(update_fields=["quantity"])
            return

        # session
        sid = str(stockrecord_id)
        self.session_cart[sid] = {"quantity": quantity}
        self._save_session()

    # ---------------- remove item ----------------
    @transaction.atomic
    def remove_item(self, stockrecord_id: int) -> None:
        if self.user:
            cart = self.get_cart_object()
            CartItem.objects.filter(cart=cart, stockrecord_id=stockrecord_id).delete()
            return
        sid = str(stockrecord_id)
        if sid in self.session_cart:
            self.session_cart.pop(sid)
            self._save_session()

    # ---------------- clear cart ----------------
    @transaction.atomic
    def clear_cart(self) -> None:
        if self.user:
            cart = self.get_cart_object()
            cart.items.all().delete()
            return
        self.session_cart.clear()
        self._save_session()