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
            'fields': ('imsi', 'msisdn',)
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
        ('Subscriber Status & Operator Determined Barring', {
            'fields': ('subscriber_status', 'operator_determined_barring')
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.msisdn:
            form.base_fields['msisdn'].initial = ', '.join(obj.msisdn)
        return form
