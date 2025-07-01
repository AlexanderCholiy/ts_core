from django.contrib import admin

from .constants import MAX_USERS_PER_PAGE
from .models import User


admin.site.empty_value_display = 'Не задано'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('is_staff',)
    ordering = ('email',)
    list_per_page = MAX_USERS_PER_PAGE
    filter_horizontal = ('user_permissions', 'groups',)
    list_editable = (
        'username',
        'first_name',
        'last_name',
    )
