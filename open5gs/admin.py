from django.contrib import admin
from .models import Subscriber

from .constants import MAX_SUBSCRIBER_PER_PAGE


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('imsi',)
    list_per_page = MAX_SUBSCRIBER_PER_PAGE
    # readonly_fields = ('security',)
