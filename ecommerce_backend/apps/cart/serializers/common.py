from rest_framework import serializers
from apps.products.models import Product, ProductVariant
from apps.products.serializers.public import VariantOptionValueSerializer
from apps.inventory.models import StockRecord

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'main_image', 'brand')

class ProductVariantSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    option_values = VariantOptionValueSerializer(many=True, read_only=True)

    class Meta:
        model = ProductVariant
        fields = ('id', 'product', 'option_values')

class StockRecordSerializer(serializers.ModelSerializer):
    product_variant = ProductVariantSerializer(read_only=True)

    class Meta:
        model = StockRecord
        fields = ('id', 'warehouse', 'product_variant', 'is_available', 'available_quantity', 'sales_price')
