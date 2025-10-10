from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer

from apps.inventory.serializers.public import StockRecordSerializer
from apps.products.models import (
    Image, ProductImage, Product,
    Category, Option, OptionValue,
    ProductVariant, VariantOptionValue,
    Attribute, AttributeValue, ProductAttributeValue,
    ProductBrand
)


class ReadOnlyModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.read_only = True


class CategoryTreeSerializer(ReadOnlyModelSerializer):
    children = serializers.SerializerMethodField()
    has_children = serializers.SerializerMethodField()

    def get_children(self, obj):
        return CategoryTreeSerializer(obj.get_children(), many=True).data

    def get_has_children(self, obj):
        return obj.numchild > 0

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'has_children', 'numchild', 'children', 'path', 'depth')


class CategoryNodeSerializer(ReadOnlyModelSerializer):
    children = serializers.SerializerMethodField()
    has_children = serializers.SerializerMethodField()

    def get_children(self, obj):
        return CategoryTreeSerializer(obj.get_children().order_by('path'), many=True).data

    def get_has_children(self, obj):
        return obj.numchild > 0

    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'slug', 'has_children', 'numchild', 'children',
                  'path', 'depth')


class ImageSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'file', 'width', 'height')


class ProductImageSerializer(ReadOnlyModelSerializer):
    image = ImageSerializer()

    class Meta:
        model = ProductImage
        fields = ('id', 'order', 'alt_text', 'image')


class MainImageSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id',)


class OptionValueSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = OptionValue
        fields = ('id', 'value')


class OptionSerializer(ReadOnlyModelSerializer):
    values = OptionValueSerializer(many=True, read_only=True)

    class Meta:
        model = Option
        fields = ('id', 'name', 'values')


class VariantOptionValueSerializer(ReadOnlyModelSerializer):
    option = OptionSerializer(read_only=True)
    selected_value = OptionValueSerializer(source='value',read_only=True)

    class Meta:
        model = VariantOptionValue
        fields = ('id', 'option', 'selected_value')


class ProductVariantSerializer(ReadOnlyModelSerializer):
    option_values = VariantOptionValueSerializer(many=True, read_only=True)
    stockrecords = StockRecordSerializer(many=True, read_only=True)
    total_available_quantity = serializers.SerializerMethodField()

    def get_total_available_quantity(self, obj):
        return obj.total_available_quantity

    class Meta:
        model = ProductVariant
        fields = ('id', 'sku', 'option_values', 'stockrecords', 'is_available', 'total_available_quantity')


class MainVariantSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ('id',)


class AttributeValueSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = AttributeValue
        fields = ('id', 'value')


class AttributeSerializer(ReadOnlyModelSerializer):
    values = AttributeValueSerializer(many=True, read_only=True)

    class Meta:
        model = Attribute
        fields = ('id', 'name', 'values')


class ProductAttributeValueSerializer(ReadOnlyModelSerializer):
    attribute = AttributeSerializer(read_only=True)
    selected_value = AttributeValueSerializer(source='value', read_only=True)


    class Meta:
        model = ProductAttributeValue
        fields = ('id', 'attribute', 'selected_value')


class ProductBrandSerializer(TaggitSerializer, ReadOnlyModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = ProductBrand
        fields = ('id', 'name', 'description', 'slug', 'website', 'tags')



class ProductSerializer(ReadOnlyModelSerializer):
    category = CategoryTreeSerializer(read_only=True)
    brand = ProductBrandSerializer(read_only=True)
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






