from django.contrib import admin
from .models import Product, ProductType, Attribute, AttributeValue, ProductAttributeValue, Image, ProductImage, \
    Option, OptionValue

admin.site.register(AttributeValue)
admin.site.register(OptionValue)
admin.site.register(ProductAttributeValue)
admin.site.register(Image)
admin.site.register(ProductImage)


class AttributeInline(admin.TabularInline):
    model = Attribute
    extra = 2


class OptionInline(admin.TabularInline):
    model = Option
    extra = 2


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name', )
    inlines = [AttributeInline, OptionInline]


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 2


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_type')
    inlines = [AttributeValueInline]


class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 2


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_type')
    inlines = [ProductAttributeValueInline, ProductImageInline]


class OptionValueInline(admin.TabularInline):
    model = OptionValue
    extra = 2


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_type')
    inlines = [OptionValueInline]