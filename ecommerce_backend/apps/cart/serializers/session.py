from rest_framework import serializers
from .common import StockRecordSerializer

class CartItemSessionSerializer(serializers.Serializer):
    stockrecord = StockRecordSerializer(read_only=True)
    quantity = serializers.IntegerField()
    unit_price = serializers.IntegerField()
    total_price = serializers.IntegerField()


class CartSessionSerializer(serializers.Serializer):
    items = CartItemSessionSerializer(many=True)
    total_items = serializers.IntegerField()
    total_price = serializers.IntegerField()
