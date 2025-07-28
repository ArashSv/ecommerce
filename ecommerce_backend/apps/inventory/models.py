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


