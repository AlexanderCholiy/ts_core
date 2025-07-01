from django.contrib import admin

from .models import Status, Pole, Operator, Modem
from .constants import (
    MAX_STATUS_PER_PAGE,
    MAX_OPERATOR_PER_PAGE,
    MAX_POLE_PER_PAGE,
    MAX_MODEM_PER_PAGE,
)


admin.site.empty_value_display = 'Не задано'


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'description',)
    list_editable = ('description',)
    search_fields = ('description',)
    list_per_page = MAX_STATUS_PER_PAGE
    ordering = ('id',)


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'st_name',)
    list_editable = ('name', 'st_name',)
    search_fields = ('name',)
    list_per_page = MAX_OPERATOR_PER_PAGE
    ordering = ('id',)


@admin.register(Pole)
class PoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'address', 'latitude', 'longitude', 'status',)
    list_editable = ('status',)
    search_fields = ('id',)
    list_per_page = MAX_POLE_PER_PAGE
    ordering = ('id',)
    list_filter = ('status',)
    autocomplete_fields = (
        'status', 'operator_1', 'operator_2', 'operator_3', 'contractor',
    )


@admin.register(Modem)
class ModemAdmin(admin.ModelAdmin):
    list_display = (
        'pole_1',
        'id',
        'serial',
        'mac',
        'level',
        'status',
        'watchdog',
        'latitude',
        'longtitude',
        'version',
        'firmware',
        'cabinet_serial',
        'status_timestamp',
    )
    list_editable = ('status',)
    search_fields = ('id', 'mac', 'pole_1', 'pole_2', 'pole_3',)
    list_per_page = MAX_MODEM_PER_PAGE
    ordering = ('pole_1',)
    list_filter = ('level', 'status',)
    autocomplete_fields = (
        'status', 'pole_1', 'pole_2', 'pole_3',
    )
