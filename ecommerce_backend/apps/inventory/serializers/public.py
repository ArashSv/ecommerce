from rest_framework import serializers
from apps.inventory.models import Warehouse, StockRecord


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ('id', 'name', 'province', 'city', 'postal_address',
                  'postal_code', 'plaque', 'unit')
        read_only_fields = fields


class StockRecordSerializer(serializers.ModelSerializer):
    warehouse = WarehouseSerializer(read_only=True)

    class Meta:
        model = StockRecord
        fields = ('id','warehouse','product_variant','quantity', 'sales_price')