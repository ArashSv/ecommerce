from django.contrib import admin
from .models import Product, ProductType, Attribute, AttributeValue, ProductAttributeValue

admin.site.register(AttributeValue)
admin.site.register(ProductAttributeValue)


class AttributeInline(admin.TabularInline):
    model = Attribute
    extra = 2


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name', )
    inlines = [AttributeInline]


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


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_type')
    inlines = [ProductAttributeValueInline]