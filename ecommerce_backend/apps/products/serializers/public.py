from rest_framework import serializers
from rest_framework import serializers
from apps.products.models import (
    Image, ProductImage, Product,
    Category, Option, OptionValue,
    ProductVariant, VariantOptionValue
)


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


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'file', 'width', 'height')


class ProductImageSerializer(serializers.ModelSerializer):
    image = ImageSerializer()

    class Meta:
        model = ProductImage
        fields = ('order', 'alt_text', 'image')


class OptionValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionValue
        fields = ('id', 'value')
        read_only_fields = fields


class OptionSerializer(serializers.ModelSerializer):
    values = OptionValueSerializer(many=True, read_only=True)

    class Meta:
        model = Option
        fields = ('id', 'name', 'values')
        read_only_fields = fields


class VariantOptionValueSerializer(serializers.ModelSerializer):
    option = OptionSerializer(read_only=True)
    selected_value = OptionValueSerializer(source='value',read_only=True)

    class Meta:
        model = VariantOptionValue
        fields = ('option', 'selected_value')
        read_only_fields = fields


class ProductVariantSerializer(serializers.ModelSerializer):
    option_values = VariantOptionValueSerializer(many=True, read_only=True)

    class Meta:
        model = ProductVariant
        fields = ('id', 'option_values')
        read_only_fields = fields