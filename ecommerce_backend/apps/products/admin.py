from django.contrib import admin
from .models import ProductType, Attribute


class AttributeInline(admin.TabularInline):
    model = Attribute
    extra = 2


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name', )
    inlines = [AttributeInline]


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_type')