from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models

from .manager import UserManager

mobile_regex = RegexValidator(regex=r'^09\d{9}$', message="Phone number must be 11 digits and start with 09.")

class User(AbstractBaseUser):
    mobile_number = models.CharField(validators=[mobile_regex], max_length=11, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)

    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_ban = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "mobile_number"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.mobile_number}"

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    @property
    def is_staff(self):
        return self.is_superuser