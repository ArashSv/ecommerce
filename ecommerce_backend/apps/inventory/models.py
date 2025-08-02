from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Warehouse(BaseModel):
    name = models.CharField(max_length=64)

    province = models.CharField(max_length=64, null=True, blank=True)
    city = models.CharField(max_length=64, null=True, blank=True)

    postal_address = models.TextField(null=True, blank=True)
    postal_code = models.IntegerField(null=True, blank=True)
    plaque = models.IntegerField(null=True, blank=True)
    unit = models.CharField(max_length=4, null=True, blank=True)  # exam : 30B, 2A, ..

    # Geolocation coordinates of the address
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    def __str__(self):
        return self.name


class StockRecord(BaseModel):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stockrecords')
    product_variant = models.ForeignKey('products.ProductVariant', on_delete=models.CASCADE, related_name='stockrecords')
    sku = models.CharField(max_length=64, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    reserved_quantity = models.PositiveIntegerField()
    reorder_threshold = models.PositiveIntegerField(null=True, blank=True)
    buy_price = models.PositiveBigIntegerField(null=True, blank=True)
    sales_price = models.PositiveBigIntegerField()

    @property
    def available_quantity(self):
        return max(self.quantity - self.reserved_quantity, 0)

    def __str__(self):
        return f"{self.warehouse} : {self.product_variant}({self.available_quantity})"