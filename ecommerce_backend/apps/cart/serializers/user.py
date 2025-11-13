from rest_framework import serializers
from .common import StockRecordSerializer
from apps.cart.models import CartItem, Cart


class CartItemUserSerializer(serializers.ModelSerializer):
    stockrecord = StockRecordSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ('stockrecord', 'quantity', 'unit_price', 'total_price')


class CartUserSerializer(serializers.ModelSerializer):
    items = CartItemUserSerializer(source='items.all', many=True)
    total_items = serializers.IntegerField()
    total_price = serializers.IntegerField()

    class Meta:
        model = Cart
        fields = ('items', 'total_items', 'total_price')
