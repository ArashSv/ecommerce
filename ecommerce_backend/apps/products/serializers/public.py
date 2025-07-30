from rest_framework import serializers

from ecommerce_backend.apps.products.models import Category


class CategoryTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        return CategoryTreeSerializer(obj.get_children(), many=True).data

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'children')


class CategoryNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'