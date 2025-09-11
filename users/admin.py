from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .constants import MAX_USERS_PER_PAGE
from .models import PendingUser, User

admin.site.empty_value_display = 'Не задано'


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'username', 'avatar', 'role', 'date_of_birth')


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('email', 'username', 'avatar', 'role', 'date_of_birth')


@admin.register(User)
class BaseUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'role',
        'is_active',
        'is_staff',
    )
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    list_editable = ('role', 'is_active')

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (
            'Личная информация',
            {'fields': ('first_name', 'last_name', 'avatar', 'date_of_birth')}
        ),
        (
            'Права',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                    'role',
                )
            }
        ),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'username',
                'avatar',
                'role',
                'password1',
                'password2',
                'is_staff',
                'is_active',
            ),
        }),
    )

    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)


@admin.register(PendingUser)
class PendingUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'last_login')
    search_fields = ('email', 'username')
    ordering = ('email',)
    list_per_page = MAX_USERS_PER_PAGE
