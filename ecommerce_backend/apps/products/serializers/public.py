from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer

from apps.inventory.serializers.public import StockRecordSerializer
from apps.products.models import (
    Image, ProductImage, Product,
    Category, Option, OptionValue,
    ProductVariant, VariantOptionValue,
    Attribute, AttributeValue, ProductAttributeValue
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


class MainImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id',)


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
    stockrecords = StockRecordSerializer(many=True, read_only=True)
    total_available_quantity = serializers.SerializerMethodField()

    def get_total_available_quantity(self, obj):
        return obj.total_available_quantity

    class Meta:
        model = ProductVariant
        fields = ('id', 'sku', 'option_values', 'stockrecords', 'is_available', 'total_available_quantity')
        read_only_fields = fields


class MainVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ('id',)


class AttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        fields = ('id', 'value')
        read_only_fields = fields


class AttributeSerializer(serializers.ModelSerializer):
    values = AttributeValueSerializer(many=True, read_only=True)

    class Meta:
        model = Attribute
        fields = ('id', 'name', 'values')
        read_only_fields = fields


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    attribute = AttributeSerializer(read_only=True)
    selected_value = AttributeValueSerializer(source='value', read_only=True)


    class Meta:
        model = ProductAttributeValue
        fields = ('attribute', 'selected_value')
        read_only_fields = fields


class ProductSerializer(serializers.ModelSerializer):
    category = CategoryTreeSerializer(many=True, read_only=True)
    attribute_values = ProductAttributeValueSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    product_images = ProductImageSerializer(many=True, read_only=True)
    tags = TagListSerializerField()

    main_image_id = serializers.SerializerMethodField()
    main_variant_id = serializers.SerializerMethodField()

    def get_main_image_id(self, obj):
        return MainImageSerializer(obj.main_image).data

    def get_main_variant_id(self, obj):
        return MainVariantSerializer(obj.main_variant).data

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'brand',
            'slug',
            'meta_title',
            'meta_description',
            'category',
            'description',
            'tags',
            'attribute_values',
            'variants',
            'main_variant_id',
            'product_images',
            'main_image_id',
        )
        read_only_fields = fields





