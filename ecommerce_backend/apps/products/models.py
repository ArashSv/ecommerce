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


class ProductImage(BaseModel):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField()
    alt_text = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        unique_together = ('product', 'order',
                           'product', 'image')
        ordering = ('order',)


class Product(BaseModel):
    name = models.CharField(max_length=128)
    description = models.TextField()
    images = models.ManyToManyField(Image, through=ProductImage, related_name='products')

