from rest_framework import serializers

class AddItemInputSerializer(serializers.Serializer):
    stockrecord_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)

class UpdateQuantityInputSerializer(serializers.Serializer):
    stockrecord_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=0)

class RemoveItemInputSerializer(serializers.Serializer):
    stockrecord_id = serializers.IntegerField()
