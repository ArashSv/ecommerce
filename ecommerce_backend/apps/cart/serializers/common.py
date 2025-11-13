from rest_framework import serializers
from apps.products.models import Product, ProductVariant
from apps.inventory.models import StockRecord

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'main_image', 'brand')

class ProductVariantSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = ProductVariant
        fields = ('id', 'options', 'product')

class StockRecordSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)

    class Meta:
        model = StockRecord
        fields = ('id', 'warehouse', 'variant', 'is_available', 'available_quantity', 'sales_price')
