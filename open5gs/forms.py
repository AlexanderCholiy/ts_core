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
from .schemas import MSISDN_SCHEMA, SECURITY_SCHEMA, AMBR_SCHEMA, SLICE_SCHEMA
from .utils import MongoJSONEncoder


class SubscriberForm(forms.ModelForm):
    msisdn = forms.JSONField(
        required=False,
        widget=JSONFormWidget(schema=MSISDN_SCHEMA),
        help_text='Список номеров MSISDN',
        encoder=MongoJSONEncoder,
    )
    security = forms.JSONField(
        widget=JSONFormWidget(schema=SECURITY_SCHEMA),
        help_text='Настройка безопасности',
        encoder=MongoJSONEncoder,
    )
    ambr = forms.JSONField(
        widget=JSONFormWidget(schema=AMBR_SCHEMA),
        help_text='Настройки максимальной скорости передачи данных',
        encoder=MongoJSONEncoder,
    )
    slice = forms.JSONField(
        widget=JSONFormWidget(schema=SLICE_SCHEMA),
        help_text='Список конфигураций сетевых срезов',
        initial=[],
        encoder=MongoJSONEncoder,
    )

    class Meta:
        model = Subscriber
        fields = ('imsi', 'subscriber_status', 'operator_determined_barring')

    def clean_msisdn(self):
        msisdn = self.cleaned_data.get('msisdn', [])

        if not isinstance(msisdn, list):
            raise ValidationError('MSISDN должен быть списком')

        for number in msisdn:
            if not isinstance(number, str):
                raise ValidationError('Каждый MSISDN должен быть строкой')
            if not number.isdigit():
                raise ValidationError(
                    f'MSISDN {number} должен содержать только цифры'
                )
            if len(number) > MAX_SUBSCRIBER_MSISDN_LEN:
                raise ValidationError(
                    f'MSISDN {number} не должен превышать '
                    f'{MAX_SUBSCRIBER_MSISDN_LEN} символов'
                )

        if len(msisdn) != len(set(msisdn)):
            raise ValidationError('MSISDN должны быть уникальными')

        return msisdn

    def clean_security(self):
        security_data = self.cleaned_data.get('security', {})

        if not all(k in security_data for k in ['k', 'amf']):
            raise ValidationError(
                'Поля "Subscriber Key (K)" и '
                '"Authentication Management Field (AMF)" обязательны для '
                'заполнения'
            )

        hex_fields = [
            ('k', 'Subscriber Key (K)'),
            ('amf', 'Authentication Management Field (AMF)'),
            ('op', 'USIM Type: OP'),
            ('opc', 'USIM Type: OPc'),
        ]
        for field, name in hex_fields:
            if (
                field in security_data
                and not hexadecimal_validator(security_data[field])
            ):
                raise ValidationError(f'Поле {name} должно быть в hex-формате')

        if 'op' in security_data and 'opc' in security_data:
            raise ValidationError(
                'Можно указать только OP или OPc, но не оба'
            )

        return security_data

    def clean_ambr(self):
        ambr_data = self.cleaned_data.get('ambr', {})

        if not all(k in ambr_data for k in ['downlink', 'uplink']):
            raise ValidationError(
                'Необходимо указать downlink и uplink для AMBR'
            )

        for direction in ['downlink', 'uplink']:
            if (
                'value' not in ambr_data[direction]
                or 'unit' not in ambr_data[direction]
            ):
                raise ValidationError(
                    f'Для {direction} необходимо указать значение и единицу '
                    'измерения'
                )

        return ambr_data
