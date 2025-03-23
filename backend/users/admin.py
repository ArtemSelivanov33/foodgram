from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

from foodgram_backend.constants import ADDITIONAL_USER_FIELDS

User = get_user_model()


@admin.register(User)
class AdminUser(BaseUserAdmin):
    add_fieldsets = BaseUserAdmin.add_fieldsets + ADDITIONAL_USER_FIELDS
    fieldsets = BaseUserAdmin.fieldsets + ADDITIONAL_USER_FIELDS
