from django.contrib import admin

from .constants import MAX_USERS_PER_PAGE
from .models import User, PendingUser


admin.site.empty_value_display = 'Не задано'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email', 'username', 'first_name', 'last_name', 'role', 'is_active'
    )
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('role',)
    ordering = ('email',)
    list_per_page = MAX_USERS_PER_PAGE
    filter_horizontal = ('user_permissions', 'groups',)
    list_editable = (
        'username',
        'first_name',
        'last_name',
        'role',
    )


@admin.register(PendingUser)
class PendingUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'last_login')
    search_fields = ('email', 'username')
    ordering = ('email',)
    list_per_page = MAX_USERS_PER_PAGE
