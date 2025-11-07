from rest_framework import serializers
from taggit.models import Tag
from apps.products.services import product_variants, utils
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


class TagSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


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
    parent = serializers.SerializerMethodField()
    ancestors = serializers.SerializerMethodField()


    def get_parent(self, obj):
        parent = obj.get_parent()
        if not parent:
            return None
        return {
            'id': parent.id,
            'name': parent.name,
            'slug': parent.slug,
            'path': parent.path,
            'depth': parent.depth,
        }

    def get_ancestors(self, obj):
        ancestors_qs = obj.get_ancestors()
        return [
            {
                'id': a.id,
                'name': a.name,
                'slug': a.slug,
                'path': a.path,
                'depth': a.depth,
            }
            for a in ancestors_qs
        ]

    def get_children(self, obj):
        return CategoryTreeSerializer(obj.get_children(), many=True).data

    def get_has_children(self, obj):
        return obj.numchild > 0


    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'slug', 'parent', 'ancestors', 'has_children', 'numchild', 'children',
                  'path', 'depth')


class ProductCategorySerializer(ReadOnlyModelSerializer):
    parent = serializers.SerializerMethodField()
    ancestors = serializers.SerializerMethodField()

    def get_parent(self, obj):
        parent = obj.get_parent()
        if not parent:
            return None
        return {
            'id': parent.id,
            'name': parent.name,
            'slug': parent.slug,
            'path': parent.path,
            'depth': parent.depth,
        }

    def get_ancestors(self, obj):
        return [
            {
                'id': a.id,
                'name': a.name,
                'slug': a.slug,
                'path': a.path,
                'depth': a.depth,
            }
            for a in obj.get_ancestors()
        ]

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'path', 'depth', 'parent', 'ancestors')


class ImageSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'file', 'width', 'height')


class ProductImageSerializer(ReadOnlyModelSerializer):
    image = ImageSerializer()

    class Meta:
        model = ProductImage
        fields = ('id', 'order', 'alt_text', 'image')


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


class ProductVariantSummarySerializer(ReadOnlyModelSerializer):
    main_stockrecord = serializers.SerializerMethodField()

    def get_main_stockrecord(self, obj):
        return StockRecordSerializer(obj.main_stockrecord).data

    class Meta:
        model = ProductVariant
        fields = ('id', 'is_available', 'main_stockrecord')


class ProductVariantSerializer(ReadOnlyModelSerializer):
    option_values = VariantOptionValueSerializer(many=True, read_only=True)
    stockrecords = StockRecordSerializer(many=True, read_only=True)
    main_stockrecord = serializers.SerializerMethodField()
    total_available_quantity = serializers.SerializerMethodField()

    def get_main_stockrecord(self, obj):
        return StockRecordSerializer(obj.main_stockrecord).data

    def get_total_available_quantity(self, obj):
        return obj.total_available_quantity

    class Meta:
        model = ProductVariant
        fields = ('id', 'sku', 'is_available', 'option_values', 'main_stockrecord', 'stockrecords',
                  'total_available_quantity')


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


class ProductBrandSerializer(ReadOnlyModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = ProductBrand
        fields = ('id', 'name', 'description', 'slug', 'website', 'tags')


class ProductListSerializer(ReadOnlyModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    brand = ProductBrandSerializer(read_only=True)
    attribute_values = ProductAttributeValueSerializer(many=True, read_only=True)
    main_image = serializers.SerializerMethodField()
    main_variant = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)

    def get_main_image(self, obj):
        return ProductImageSerializer(obj.main_image).data

    def get_main_variant(self, obj):
        return ProductVariantSummarySerializer(obj.main_variant).data

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'brand',
            'slug',
            'category',
            'description',
            'tags',
            'attribute_values',
            'main_variant',
            'main_image',
        )


class ProductDetailSerializer(ReadOnlyModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    brand = ProductBrandSerializer(read_only=True)
    attribute_values = ProductAttributeValueSerializer(many=True, read_only=True)
    variants = serializers.SerializerMethodField()
    selected_variant = serializers.SerializerMethodField()
    product_images = ProductImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True)

    main_image = serializers.SerializerMethodField()
    main_variant = serializers.SerializerMethodField()

    def get_variants(self, obj):
        request = self.context.get('request')
        options_dict = utils.parse_options_query(request.query_params.get('options')) if request else {}

        if options_dict:
            qs = product_variants.filter_variants_by_options(obj, options_dict)
        else:
            qs = obj.variants.all()

        return ProductVariantSerializer(qs, many=True).data

    def get_main_image(self, obj):
        return ProductImageSerializer(obj.main_image).data

    def get_main_variant(self, obj):
        return ProductVariantSerializer(obj.main_variant).data

    def get_selected_variant(self, obj):
        request = self.context.get('request')
        if not request:
            return ProductVariantSerializer(obj.main_variant).data

        variant = self._get_variant_by_id(obj, request.query_params.get('variant_id'))
        if variant:
            return ProductVariantSerializer(variant).data

        variant = self._get_variant_by_options(obj, request.query_params.get('options'))
        if variant:
            return ProductVariantSerializer(variant).data

        return ProductVariantSerializer(obj.main_variant).data

    def _get_variant_by_id(self, obj, variant_id):
        if not variant_id or not str(variant_id).isdigit():
            return None
        try:
            return obj.variants.get(id=int(variant_id))
        except ProductVariant.DoesNotExist:
            return None

    def _get_variant_by_options(self, obj, options_query):
        if not options_query:
            return None
        options_dict = utils.parse_options_query(options_query)
        if not options_dict:
            return None

        variants = product_variants.filter_variants_by_options(obj, options_dict)
        return variants.first() if variants.exists() else None

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
            'main_variant',
            'selected_variant',
            'product_images',
            'main_image',
        )

