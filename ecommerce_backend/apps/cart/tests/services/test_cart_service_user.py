from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from apps.products.models import ProductType, Product, ProductVariant
from apps.inventory.models import Warehouse, StockRecord
from apps.cart.models import Cart, CartItem
from apps.cart.services import CartService

User = get_user_model()


class CartServiceUserTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(mobile_number="testuser", password="password")

        self.product_type = ProductType.objects.create(name="Simple")
        self.product = Product.objects.create(name="Test Product", product_type=self.product_type)
        self.variant = ProductVariant.objects.create(product=self.product, sku="TESTSKU")
        self.warehouse = Warehouse.objects.create(name='ahvaz')
        self.stock = StockRecord.objects.create(
            product_variant=self.variant,
            sales_price=100,
            quantity=10,
            reserved_quantity=5,
            warehouse=self.warehouse
        )
        self.cart_service = CartService(user=self.user)

    def test_get_cart_object_creates_if_not_exist(self):
        cart = self.cart_service.get_cart_object()
        self.assertIsInstance(cart, Cart)
        self.assertEqual(cart.user, self.user)
        cart2 = self.cart_service.get_cart_object()
        self.assertEqual(cart.pk, cart2.pk)

    def test_add_item_creates_cartitem(self):
        self.cart_service.add_item(self.stock.id, quantity=3)
        cart = self.cart_service.get_cart_object()
        item = CartItem.objects.get(cart=cart, stockrecord=self.stock)
        self.assertEqual(item.quantity, 3)

    def test_add_item_increments_existing_cartitem(self):
        self.cart_service.add_item(self.stock.id, quantity=2)
        self.cart_service.add_item(self.stock.id, quantity=3)
        cart = self.cart_service.get_cart_object()
        item = CartItem.objects.get(cart=cart, stockrecord=self.stock)
        self.assertEqual(item.quantity, 5)

    def test_add_item_more_than_available_raises(self):
        with self.assertRaises(DjangoValidationError):
            self.cart_service.add_item(self.stock.id, quantity=20)

    def test_add_item_invalid_stock_raises(self):
        with self.assertRaises(DjangoValidationError):
            self.cart_service.add_item(stockrecord_id=9999, quantity=1)

    def test_add_item_zero_or_negative_quantity_raises(self):
        with self.assertRaises(DjangoValidationError):
            self.cart_service.add_item(self.stock.id, quantity=0)
        with self.assertRaises(DjangoValidationError):
            self.cart_service.add_item(self.stock.id, quantity=-5)

    def test_update_quantity_changes_quantity(self):
        self.cart_service.add_item(self.stock.id, quantity=2)
        self.cart_service.update_quantity(self.stock.id, quantity=5)
        item = CartItem.objects.get(cart=self.cart_service.get_cart_object(), stockrecord=self.stock)
        self.assertEqual(item.quantity, 5)

    def test_update_quantity_more_than_available_raises(self):
        self.cart_service.add_item(self.stock.id, quantity=2)
        with self.assertRaises(DjangoValidationError):
            self.cart_service.update_quantity(self.stock.id, quantity=20)

    def test_update_quantity_to_zero_removes_item(self):
        self.cart_service.add_item(self.stock.id, quantity=2)
        self.cart_service.update_quantity(self.stock.id, quantity=0)
        cart = self.cart_service.get_cart_object()
        self.assertFalse(CartItem.objects.filter(cart=cart, stockrecord=self.stock).exists())

    def test_update_quantity_item_not_in_cart_raises(self):
        with self.assertRaises(DjangoValidationError):
            self.cart_service.update_quantity(self.stock.id, quantity=1)

    def test_remove_item_deletes_cartitem(self):
        self.cart_service.add_item(self.stock.id, quantity=3)
        self.cart_service.remove_item(self.stock.id)
        cart = self.cart_service.get_cart_object()
        self.assertFalse(CartItem.objects.filter(cart=cart, stockrecord=self.stock).exists())

    def test_clear_cart_removes_all_items(self):
        warehouse = Warehouse.objects.create(name='dezful')
        stock2 = StockRecord.objects.create(
            product_variant=self.variant, quantity=5, sales_price=50, reserved_quantity=0,
            warehouse=warehouse
        )
        self.cart_service.add_item(self.stock.id, quantity=2)
        self.cart_service.add_item(stock2.id, quantity=3)

        self.cart_service.clear_cart()
        cart = self.cart_service.get_cart_object()
        self.assertEqual(cart.items.count(), 0)

    def test_get_totals_returns_correct_values(self):
        warehouse = Warehouse.objects.create(name='dezful')
        stock2 = StockRecord.objects.create(
            product_variant=self.variant, quantity=5, sales_price=50, reserved_quantity=0,
            warehouse=warehouse
        )
        self.cart_service.add_item(self.stock.id, quantity=2)  # 2*100=200
        self.cart_service.add_item(stock2.id, quantity=3)  # 3*50=150
        totals = self.cart_service.get_totals()
        self.assertEqual(totals["total_items"], 5)
        self.assertEqual(totals["total_price"], 350)

    def test_add_item_respects_available_quantity_concurrently(self):
        self.cart_service.add_item(self.stock.id, quantity=5)

        with self.assertRaises(DjangoValidationError):
            self.cart_service.add_item(self.stock.id, quantity=6)
