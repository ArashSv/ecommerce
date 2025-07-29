from django.contrib import admin
from .models import ProductType, Attribute, AttributeValue

admin.site.register(AttributeValue)


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