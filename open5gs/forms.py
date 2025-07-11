from django import forms
from django.core.exceptions import ValidationError
from django_jsonform.widgets import JSONFormWidget

from .models import Subscriber
from .constants import (
    UNIT_CHOICES, MIN_SST_VALUE, MAX_SST_VALUE, SESSION_TYPE_CHOICES,
    QOS_INDEX_CHOICES, MIN_PRIORITY_LEVEL_VALUE, MAX_PRIORITY_LEVEL_VALUE,
    EMPTION_CHOICES, MAX_SUBSCRIBER_HEX_LEN, SD_LEN, MAX_SUBSCRIBER_MSISDN_LEN
)
from .schemas import MSISDN_SCHEMA, SECURITY_SCHEMA, AMBR_SCHEMA, SLICE_SCHEMA
from .utils import MongoJSONEncoder
from .validators import validate_hex_value, validate_session, validate_br


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

    def clean(self):
        cleaned_data: dict = super().clean()
        slice_items: list[dict] = cleaned_data['slice']
        default_indicator = None

        for slice_item in slice_items:
            if not MIN_SST_VALUE <= slice_item['sst'] <= MAX_SST_VALUE:
                raise ValidationError(
                    f'SST должен быть между {MIN_SST_VALUE} и '
                    f'{MAX_SST_VALUE}'
                )

            if slice_item.get('sd'):
                validate_hex_value(slice_item['sd'], 'SD', SD_LEN, SD_LEN)

            if slice_item.get('default_indicator') is None:
                raise ValidationError(
                    'В каждом Slice необходимо указать Default S-NSSAI')

            if not isinstance(slice_item['default_indicator'], bool):
                raise ValidationError(
                    'Default S-NSSAI должен принимать булево значение')

            if slice_item['default_indicator'] is True:
                default_indicator = True

            for session in slice_item['session']:
                validate_session(session)

        if default_indicator is None:
            raise ValidationError(
                'Требуется как минимум 1 Default S-NSSAI')

        return cleaned_data

    def clean_msisdn(self):
        msisdn = self.cleaned_data.get('msisdn')

        if not isinstance(msisdn, list):
            raise ValidationError('MSISDN должен быть списком')

        for number in msisdn:
            if not isinstance(number, str):
                raise ValidationError('Каждый MSISDN должен быть строкой')
            if not number.isdigit():
                raise ValidationError(
                    f'MSISDN {number} должен содержать только цифры')
            if len(number) > MAX_SUBSCRIBER_MSISDN_LEN:
                raise ValidationError(
                    f'MSISDN {number} не должен превышать '
                    f'{MAX_SUBSCRIBER_MSISDN_LEN} символов'
                )

        if len(msisdn) != len(set(msisdn)):
            raise ValidationError('MSISDN должны быть уникальными')

        return msisdn

    def clean_security(self):
        security_data: dict = self.cleaned_data.get('security', {})

        if not all(k in security_data for k in ['k', 'amf']):
            raise ValidationError(
                'Поля "Subscriber Key (K)" и '
                '"Authentication Management Field (AMF)" обязательны'
            )

        hex_fields = [
            ('k', 'Subscriber Key (K'),
            ('amf', 'Authentication Management Field (AMF)'),
            ('op', 'Operator Key (OP)'),
            ('opc', 'Operator Key (OPc)'),
        ]
        for field, name in hex_fields:
            if field in security_data and security_data[field]:
                validate_hex_value(
                    security_data[field], name, MAX_SUBSCRIBER_HEX_LEN)

        if security_data.get('op') and security_data.get('opc'):
            raise ValidationError('Укажите только OP или OPc')

        return security_data

    def clean_ambr(self):
        ambr_data = self.cleaned_data.get('ambr', {})
        if not isinstance(ambr_data, dict):
            raise ValidationError('UE-AMBR это словарь')

        validate_br(ambr_data, 'UE-AMBR')

        return ambr_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['imsi'].disabled = True
            self.fields['imsi'].help_text = 'Нельзя изменить после создания'

        if self.instance and hasattr(self.instance, 'pk'):
            self._init_existing_instance()

    def _init_existing_instance(self):
        """Инициализация данных существующего абонента"""
        self.fields['msisdn'].initial = getattr(
            self.instance, 'msisdn', [])
        self.fields['security'].initial = getattr(
            self.instance, 'security', {})
        self.fields['ambr'].initial = getattr(
            self.instance, 'ambr', {})
        self.fields['slice'].initial = getattr(
            self.instance, 'slice', [])

    def save(self, commit=True):
        instance = super().save(commit=False)

        if instance.pk:
            current_security = getattr(instance, 'security', {})
            current_slice = getattr(instance, 'slice', [])
            cleaned_security = self.cleaned_data.get('security', {})
            if cleaned_security:
                instance.security = {**current_security, **cleaned_security}

            cleaned_slice = self.cleaned_data.get('slice', [])
            if cleaned_slice:
                for i, slice_item in enumerate(cleaned_slice):
                    if i < len(current_slice):
                        for key, value in current_slice[i].items():
                            if key not in slice_item:
                                slice_item[key] = value
                instance.slice = cleaned_slice
        else:
            instance.msisdn = self.cleaned_data.get('msisdn', [])
            instance.security = self.cleaned_data.get('security', {})
            instance.ambr = self.cleaned_data.get('ambr', {})
            instance.slice = self.cleaned_data.get('slice', [])

        if commit:
            instance.save()

        return instance
