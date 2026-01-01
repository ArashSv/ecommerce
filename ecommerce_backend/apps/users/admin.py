from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Address


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ['-date_joined']
    list_display = ['mobile_number', 'is_superuser']

    fieldsets = (
        (None, {'fields': ('mobile_number', 'password')}),
        ('Personal Info', {'fields': ('email',)}),
        ('Permissions', {'fields': ('is_active', 'is_superuser', 'is_email_verified', 'is_phone_verified')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'last_update')}),
    )

    list_filter = ("is_superuser", "is_ban", "is_active",)
    search_fields = ("mobile_number",  "email")
    ordering = ("mobile_number",)
    filter_horizontal = []

    readonly_fields = ['last_login', 'date_joined', 'last_update']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile_number', 'email', 'password1', 'password2'),
        }),
    )


admin.site.register(Address)