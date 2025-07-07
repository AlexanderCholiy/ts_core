from django.contrib import admin

from .models import Subscriber
from .forms import SubscriberForm
from .constants import MAX_SUBSCRIBER_PER_PAGE


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    form = SubscriberForm
    list_display = ('imsi',)
    list_per_page = MAX_SUBSCRIBER_PER_PAGE
    # readonly_fields = ('msisdn',)

    fieldsets = (
        (None, {
            'fields': ('imsi', 'msisdn_input',)
        }),
        ('Security', {
            'fields': (
                'security_k',
                'security_amf',
                'security_op',
                'security_opc',
                'security_sqn',
            ),
        }),
        ('Aggregate Maximum Bit Rate', {
            'fields': (
                'ambr_downlink_value',
                'ambr_downlink_unit',
                'ambr_uplink_value',
                'ambr_uplink_unit',
            )
        }),
    )
