from rest_framework import serializers
from apps.products.models import Category, Image, ProductImage, Product


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


class ProductSerializer(serializers.ModelSerializer):
    product_images = ProductImageSerializer(many=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'product_images')


