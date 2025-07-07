from django.contrib import admin

from .models import Subscriber
from .forms import SubscriberForm
from .constants import MAX_SUBSCRIBER_PER_PAGE


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    form = SubscriberForm
    list_display = ('imsi',)
    list_per_page = MAX_SUBSCRIBER_PER_PAGE

    fieldsets = (
        (None, {
            'fields': ('imsi',)
        }),
        ('Параметры безопасности', {
            'fields': (
                'security_k',
                'security_amf',
                'security_op',
                'security_opc',
                'security_sqn',
            ),
        }),
    )
