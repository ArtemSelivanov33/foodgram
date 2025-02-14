from django.contrib import admin
from django.contrib.auth import get_user_model

from user.models import Follow

User = get_user_model()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('first_name', 'last_name')
