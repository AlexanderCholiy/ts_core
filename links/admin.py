from django.contrib import admin

from links.models import ExternalResource


@admin.register(ExternalResource)
class ExternalResourceAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'url', 'is_active', 'created_at', 'updated_at'
    )

    list_editable = ('title', 'url', 'is_active')

    list_display_links = ('id',)

    search_fields = ('title', 'url')

    list_filter = ('created_at',)

    readonly_fields = ('created_at', 'updated_at')
