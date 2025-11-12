from django.test import TestCase
from django.core.exceptions import ValidationError as DjangoValidationError
from apps.products.models import ProductType, Product, ProductVariant
from apps.inventory.models import Warehouse, StockRecord
from apps.cart.services import CartService


class CartServiceSessionTests(TestCase):
    def setUp(self):
        self.session = {}
        self.product_type = ProductType.objects.create(name="Simple")
        self.product = Product.objects.create(name="Test Product", product_type=self.product_type)
        self.variant = ProductVariant.objects.create(product=self.product, sku="TESTSKU")
        self.warehouse = Warehouse.objects.create(name='ahvaz')
        self.stock = StockRecord.objects.create(
            product_variant=self.variant,
            sales_price=100,
            quantity=10,
            reserved_quantity=0,
            warehouse=self.warehouse
        )
        self.cart_service = CartService(session=self.session)

    def test_session_cart_starts_empty(self):
        items = self.cart_service.get_session_items()
        self.assertEqual(items, [])
        totals = self.cart_service.get_totals()
        self.assertEqual(totals, {"total_items": 0, "total_price": 0})

    def test_add_item_creates_session_item(self):
        self.cart_service.add_item(self.stock.id, quantity=3)
        items = self.cart_service.get_session_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["quantity"], 3)
        totals = self.cart_service.get_totals()
        self.assertEqual(totals["total_items"], 3)
        self.assertEqual(totals["total_price"], 300)

    def test_add_item_increments_existing_session_item(self):
        self.cart_service.add_item(self.stock.id, quantity=2)
        self.cart_service.add_item(self.stock.id, quantity=3)
        items = self.cart_service.get_session_items()
        self.assertEqual(items[0]["quantity"], 5)
        totals = self.cart_service.get_totals()
        self.assertEqual(totals["total_items"], 5)
        self.assertEqual(totals["total_price"], 500)

    def test_add_item_more_than_available_raises(self):
        with self.assertRaises(DjangoValidationError):
            self.cart_service.add_item(self.stock.id, quantity=20)

    def test_add_item_zero_or_negative_quantity_raises(self):
        with self.assertRaises(DjangoValidationError):
            self.cart_service.add_item(self.stock.id, quantity=0)
        with self.assertRaises(DjangoValidationError):
            self.cart_service.add_item(self.stock.id, quantity=-5)

    def test_update_quantity_changes_session_item(self):
        self.cart_service.add_item(self.stock.id, quantity=2)
        self.cart_service.update_quantity(self.stock.id, quantity=5)
        items = self.cart_service.get_session_items()
        self.assertEqual(items[0]["quantity"], 5)
        totals = self.cart_service.get_totals()
        self.assertEqual(totals["total_items"], 5)
        self.assertEqual(totals["total_price"], 500)

    def test_update_quantity_more_than_available_raises(self):
        self.cart_service.add_item(self.stock.id, quantity=2)
        with self.assertRaises(DjangoValidationError):
            self.cart_service.update_quantity(self.stock.id, quantity=20)

    def test_update_quantity_to_zero_removes_session_item(self):
        self.cart_service.add_item(self.stock.id, quantity=2)
        self.cart_service.update_quantity(self.stock.id, quantity=0)
        self.assertEqual(self.cart_service.get_session_items(), [])
        totals = self.cart_service.get_totals()
        self.assertEqual(totals["total_items"], 0)
        self.assertEqual(totals["total_price"], 0)

    def test_remove_item_deletes_session_item(self):
        self.cart_service.add_item(self.stock.id, quantity=3)
        self.cart_service.remove_item(self.stock.id)
        self.assertEqual(self.cart_service.get_session_items(), [])
        totals = self.cart_service.get_totals()
        self.assertEqual(totals["total_items"], 0)
        self.assertEqual(totals["total_price"], 0)

    def test_clear_cart_removes_all_session_items(self):
        warehouse = Warehouse.objects.create(name='dezful')
        stock2 = StockRecord.objects.create(
            product_variant=self.variant, quantity=5, sales_price=50, reserved_quantity=0,
            warehouse=warehouse
        )
        self.cart_service.add_item(self.stock.id, quantity=2)
        self.cart_service.add_item(stock2.id, quantity=3)

        self.cart_service.clear_cart()
        self.assertEqual(self.cart_service.get_session_items(), [])
        totals = self.cart_service.get_totals()
        self.assertEqual(totals["total_items"], 0)
        self.assertEqual(totals["total_price"], 0)

    def test_add_item_respects_available_quantity_concurrently(self):
        self.cart_service.add_item(self.stock.id, quantity=5)
        with self.assertRaises(DjangoValidationError):
            self.cart_service.add_item(self.stock.id, quantity=6)  # 5+6=11 > 10
