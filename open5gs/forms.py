import json
from typing import Union
from django import forms
from django.core.exceptions import ValidationError
from django_jsonform.widgets import JSONFormWidget
from djongo.models import ObjectIdField

from .models import Subscriber
from .constants import MAX_SUBSCRIBER_MSISDN_LEN
from core.constants import (
    UNIT_CHOICES, MIN_SST_VALUE, MAX_SST_VALUE, SESSION_TYPE_CHOICES,
    QOS_INDEX_CHOICES, MIN_PRIORITY_LEVEL_VALUE, MAX_PRIORITY_LEVEL_VALUE, 
    EMPTION_CHOICES, MAX_SUBSCRIBER_HEX_LEN, SD_LEN
)
from .schemas import MSISDN_SCHEMA, SECURITY_SCHEMA, AMBR_SCHEMA, SLICE_SCHEMA
from .utils import MongoJSONEncoder
from .validators import validate_hex_value, validate_session


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
        cleaned_data = super().clean()

        if 'slice' in cleaned_data:
            for slice_item in cleaned_data['slice']:
                if not MIN_SST_VALUE <= slice_item['sst'] <= MAX_SST_VALUE:
                    raise ValidationError(
                        f'SST должен быть между {MIN_SST_VALUE} и {MAX_SST_VALUE}'
                    )
                
                if 'sd' in slice_item and slice_item['sd']:
                    validate_hex_value(slice_item['sd'], 'SD', SD_LEN, SD_LEN)
                
                for session in slice_item['session']:
                    validate_session(session)
        
        return cleaned_data

    def clean_msisdn(self):
        msisdn = self.cleaned_data.get('msisdn', [])
        
        if not isinstance(msisdn, list):
            raise ValidationError("MSISDN должен быть списком")
            
        for number in msisdn:
            if not isinstance(number, str):
                raise ValidationError("Каждый MSISDN должен быть строкой")
            if not number.isdigit():
                raise ValidationError(f"MSISDN {number} должен содержать только цифры")
            if len(number) > MAX_SUBSCRIBER_MSISDN_LEN:
                raise ValidationError(
                    f"MSISDN не должен превышать {MAX_SUBSCRIBER_MSISDN_LEN} символов"
                )
        
        if len(msisdn) != len(set(msisdn)):
            raise ValidationError("MSISDN должны быть уникальными")
            
        return msisdn

    def clean_security(self):
        security_data = self.cleaned_data.get('security', {})
        
        if not all(k in security_data for k in ['k', 'amf']):
            raise ValidationError("Поля 'k' и 'amf' обязательны")
            
        hex_fields = ['k', 'amf', 'op', 'opc']
        for field in hex_fields:
            if field in security_data and security_data[field]:
                validate_hex_value(security_data[field], field, MAX_SUBSCRIBER_HEX_LEN)
                
        if security_data.get('op') and security_data.get('opc'):
            raise ValidationError("Укажите только OP или OPc")
            
        return security_data

    def clean_ambr(self):
        ambr_data = self.cleaned_data.get('ambr', {})
        
        if not all(k in ambr_data for k in ['downlink', 'uplink']):
            raise ValidationError("Необходимо указать downlink и uplink")
            
        for direction in ['downlink', 'uplink']:
            if 'value' not in ambr_data[direction] or 'unit' not in ambr_data[direction]:
                raise ValidationError(f"Для {direction} укажите value и unit")
            
            # Преобразуем unit из строки в число
            unit_value = ambr_data[direction]['unit']
            for choice in UNIT_CHOICES:
                if choice[1] == unit_value:
                    ambr_data[direction]['unit'] = choice[0]
                    break
            else:
                raise ValidationError(f"Недопустимое значение unit для {direction}")
        
        return ambr_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and hasattr(self.instance, 'pk'):
            self._init_existing_instance()

    def _init_existing_instance(self):
        """Инициализация данных существующего абонента"""
        self.fields['msisdn'].initial = getattr(self.instance, 'msisdn', [])
        self.fields['security'].initial = getattr(self.instance, 'security', {})
        self.fields['ambr'].initial = getattr(self.instance, 'ambr', {})
        self.fields['slice'].initial = getattr(self.instance, 'slice', [])

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Сохраняем данные как есть (они уже прошли валидацию)
        instance.msisdn = self.cleaned_data.get('msisdn', [])
        instance.security = self.cleaned_data.get('security', {})
        instance.ambr = self.cleaned_data.get('ambr', {})
        instance.slice = self.cleaned_data.get('slice', [])
        
        if commit:
            instance.save()
            
        return instance
