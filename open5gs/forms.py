from django import forms
from django.core.exceptions import ValidationError
from django_jsonform.widgets import JSONFormWidget

from .constants import MAX_SUBSCRIBER_IMSI_LEN, MAX_SUBSCRIBER_MSISDN_LEN
from .models import Subscriber
from core.models import Security
from core.forms import SecurityForm
from core.constants import (
    MAX_SUBSCRIBER_HEX_LEN, UNIT_CHOICES, MIN_SST_VALUE, MAX_SST_VALUE,
    SD_LEN, MAX_SESSION_NAME_LEN, SESSION_TYPE_CHOICES, QOS_INDEX_CHOICES,
    MIN_PRIORITY_LEVEL_VALUE, MAX_PRIORITY_LEVEL_VALUE, EMPTION_CHOICES
)
from core.validators import hexadecimal_validator
from .utils import MSISDN_SCHEMA, SECURITY_SCHEMA, AMBR_SCHEMA, SLICE_SCHEMA


class SubscriberForm(forms.ModelForm):
    msisdn = forms.JSONField(
        required=False,
        widget=JSONFormWidget(schema=MSISDN_SCHEMA),
        help_text='Список номеров MSISDN',
    )
    security = forms.JSONField(
        widget=JSONFormWidget(schema=SECURITY_SCHEMA),
        help_text='Настройка безопасности',
    )
    ambr = forms.JSONField(
        widget=JSONFormWidget(schema=AMBR_SCHEMA),
        help_text='Настройки максимальной скорости передачи данных'
    )
    slice = forms.JSONField(
        widget=JSONFormWidget(schema=SLICE_SCHEMA),
        help_text='Список конфигураций сетевых срезов',
        initial=[]
    )

    class Meta:
        model = Subscriber
        fields = ('imsi', 'subscriber_status', 'operator_determined_barring')
