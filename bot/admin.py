from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,Transaction

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "telegram_id", "balance", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("اطلاعات تلگرام", {"fields": ("telegram_id", "balance")}),
    )

admin.site.register(Transaction)