import os
from datetime import datetime
import hashlib
from PIL import Image as PILImage
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ProductType(BaseModel):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


def image_upload_path(instance, filename):
    now = datetime.now()
    path = f"images/image_products/{now.year}/{now.month}/{now.day}/{now.hour}/{now.minute}"
    return os.path.join(path, filename)


class Image(BaseModel):
    file = models.ImageField(upload_to=image_upload_path)
    hash = models.CharField(max_length=64, editable=False)

    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.file:
            hasher = hashlib.sha256()
            for chunk in self.file.chunks():
                hasher.update(chunk)
            computed_hash = hasher.hexdigest()

            existing = Image.objects.filter(hash=computed_hash).first()

            if existing and existing.pk != self.pk:
                self.file = existing.file
                self.hash = existing.hash
                self.width = existing.width
                self.height = existing.height
                super().save(*args, **kwargs)
                return

            self.hash = computed_hash

            try:
                img = PILImage.open(self.file)
                self.width, self.height = img.size
            except Exception:
                self.width = self.height = 0

        super().save(*args, **kwargs)


class Product(BaseModel):
    product_type = models.ForeignKey(
        ProductType, on_delete=models.PROTECT, related_name='products'
    )
    name = models.CharField(max_length=128)
    description = models.TextField()
    images = models.ManyToManyField(
        Image, through='ProductImage', related_name='products'
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductImage(BaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='product_images'
    )
    image = models.ForeignKey(
        Image, on_delete=models.CASCADE, related_name='image_products'
    )
    order = models.PositiveSmallIntegerField()
    alt_text = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        unique_together = (
            ('product', 'order'),
            ('product', 'image'),
        )
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name} - Image #{self.order}"


class Attribute(BaseModel):
    product_type = models.ForeignKey(
        ProductType, on_delete=models.CASCADE, related_name='attributes'
    )
    name = models.CharField(max_length=64)

    class Meta:
        unique_together = ('product_type', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.product_type.name} | {self.name}"


class AttributeValue(BaseModel):
    attribute = models.ForeignKey(
        Attribute, on_delete=models.CASCADE, related_name='values'
    )
    value = models.CharField(max_length=128)

    class Meta:
        unique_together = ('attribute', 'value')
        ordering = ['value']

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class ProductAttributeValue(BaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='attribute_values'
    )
    attribute = models.ForeignKey(
        Attribute, on_delete=models.CASCADE
    )
    value = models.ForeignKey(
        AttributeValue, on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('product', 'attribute')

    def __str__(self):
        return f"{self.product.name} | {self.attribute.name}: {self.value.value}"


class Option(BaseModel):
    product_type = models.ForeignKey(
        ProductType, on_delete=models.CASCADE, related_name='options'
    )
    name = models.CharField(max_length=64)

    class Meta:
        unique_together = ('product_type', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.product_type.name} | {self.name}"


class OptionValue(BaseModel):
    option = models.ForeignKey(
        Option, on_delete=models.CASCADE, related_name='values'
    )
    value = models.CharField(max_length=128)

    class Meta:
        unique_together = ('option', 'value')
        ordering = ['value']

    def __str__(self):
        return f"{self.option.name}: {self.value}"


class ProductVariant(BaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='variants'
    )

    def __str__(self):
        return f"{self.product.name}"

    def available_quantity(self):
        ...


class VariantOptionValue(BaseModel):
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name='option_values'
    )
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    value = models.ForeignKey(OptionValue, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('variant', 'option')

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.value.option.id != self.option.id:
            raise ValidationError()

    def __str__(self):
        return f"{self.variant.product.name} | {self.option.name}: {self.value.value}"