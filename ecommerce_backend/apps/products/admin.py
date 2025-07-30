from django.contrib import admin
from treebeard.forms import movenodeform_factory
from treebeard.admin import TreeAdmin
from .models import Product, ProductType, Attribute, AttributeValue, ProductAttributeValue, Image, ProductImage, \
    Option, OptionValue, ProductVariant, VariantOptionValue, Category


admin.site.register(AttributeValue)
admin.site.register(ProductAttributeValue)
admin.site.register(OptionValue)
admin.site.register(Image)
admin.site.register(ProductImage)
admin.site.register(VariantOptionValue)


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


class VariantOptionValueInline(admin.TabularInline):
    model = VariantOptionValue
    extra = 2


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product',)
    inlines = [VariantOptionValueInline]


class CategoryAdmin(TreeAdmin):
    form = movenodeform_factory(Category)


admin.site.register(Category, CategoryAdmin)