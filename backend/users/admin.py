from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from foodgram_backend.constants import ADDITIONAL_USER_FIELDS

from .models import User


@admin.register(User)
class AdminUser(BaseUserAdmin):
    add_fieldsets = BaseUserAdmin.add_fieldsets + ADDITIONAL_USER_FIELDS
    fieldsets = BaseUserAdmin.fieldsets + ADDITIONAL_USER_FIELDS
