import json
from typing import Union

from django import forms
from django.core.exceptions import ValidationError
from django_jsonform.widgets import JSONFormWidget
from djongo.models import ObjectIdField

from .models import Subscriber
from core.models import Security, Ambr, AmbrLink, Slice, Session, PccRule, Qos, QosArp
from .constants import MAX_SUBSCRIBER_MSISDN_LEN
from core.constants import (
    UNIT_CHOICES, MIN_SST_VALUE, MAX_SST_VALUE, SESSION_TYPE_CHOICES,
    QOS_INDEX_CHOICES, MIN_PRIORITY_LEVEL_VALUE, MAX_PRIORITY_LEVEL_VALUE, EMPTION_CHOICES,
    MAX_SUBSCRIBER_HEX_LEN, SD_LEN
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
                for session in slice_item['session']:
                    session['type'] = self._get_choice_value(
                        session['type'], SESSION_TYPE_CHOICES, 'Session Type'
                    )

                    qos = session['qos']
                    qos['index'] = self._get_choice_value(
                        qos['index'], QOS_INDEX_CHOICES, '5QI/QCI'
                    )

                    arp = qos['arp']
                    arp['pre_emption_capability'] = self._get_choice_value(
                        arp['pre_emption_capability'],
                        EMPTION_CHOICES,
                        'Pre-emption Capability',
                    )
                    arp['pre_emption_vulnerability'] = self._get_choice_value(
                        arp['pre_emption_vulnerability'],
                        EMPTION_CHOICES,
                        'Pre-emption Vulnerability',
                    )

                    if 'pcc_rule' in session:
                        for pcc_rule in session['pcc_rule']:
                            pcc_qos = pcc_rule['qos']
                            pcc_qos['index'] = self._get_choice_value(
                                pcc_qos['index'], QOS_INDEX_CHOICES, '5QI/QCI'
                            )
                            pcc_arp = pcc_qos['arp']
                            pcc_arp['pre_emption_capability'] = (
                                self._get_choice_value(
                                    pcc_arp['pre_emption_capability'],
                                    EMPTION_CHOICES,
                                    'Pre-emption Capability'
                                )
                            )
                            pcc_arp['pre_emption_vulnerability'] = (
                                self._get_choice_value(
                                    pcc_arp['pre_emption_vulnerability'],
                                    EMPTION_CHOICES,
                                    'Pre-emption Vulnerability'
                                )
                            )

        return cleaned_data

    def _get_choice_value(
        self, value: Union[str, int], choices: tuple, field_name: str
    ):
        """Преобразует строковое значение enum в int (значение choice)"""
        if isinstance(value, int):
            valid_values = [choice[0] for choice in choices]
            if value not in valid_values:
                raise ValidationError(
                    f'Недопустимое значение для {field_name}')
            return value

        for choice in choices:
            if choice[1] == value:
                return choice[0]

        raise ValidationError(f'Недопустимое значение для {field_name}')

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
                    f"MSISDN {number} не должен превышать {MAX_SUBSCRIBER_MSISDN_LEN} символов"
                )

        if len(msisdn) != len(set(msisdn)):
            raise ValidationError("MSISDN должны быть уникальными")

        return msisdn

    def clean_security(self):
        security_data = self.cleaned_data.get('security', {})
        
        if not all(k in security_data for k in ['k', 'amf']):
            raise ValidationError("Поля 'k' и 'amf' обязательны для безопасности")
            
        hex_fields = ['k', 'amf', 'op', 'opc']
        for field in hex_fields:
            if field in security_data and security_data[field]:
                validate_hex_value(security_data[field], field, MAX_SUBSCRIBER_HEX_LEN)
                
        if 'op' in security_data and 'opc' in security_data and security_data['op'] and security_data['opc']:
            raise ValidationError("Можно указать только OP или OPc, но не оба")
            
        return security_data

    def clean_ambr(self):
        ambr_data = self.cleaned_data.get('ambr', {})
        
        if not all(k in ambr_data for k in ['downlink', 'uplink']):
            raise ValidationError("Необходимо указать downlink и uplink для AMBR")
            
        for direction in ['downlink', 'uplink']:
            if 'value' not in ambr_data[direction] or 'unit' not in ambr_data[direction]:
                raise ValidationError(f"Для {direction} необходимо указать value и unit")
            # Преобразование строкового unit в int
            ambr_data[direction]['unit'] = self._get_choice_value(
                ambr_data[direction]['unit'], UNIT_CHOICES, 'Unit'
            )
                
        return ambr_data

    def clean_slice(self):
        slice_data = self.cleaned_data.get('slice', [])
        
        if not isinstance(slice_data, list):
            raise ValidationError("Slice должен быть списком")
            
        for slice_item in slice_data:
            if 'sst' not in slice_item:
                raise ValidationError("Каждый срез должен иметь SST")
            if not (MIN_SST_VALUE <= slice_item['sst'] <= MAX_SST_VALUE):
                raise ValidationError(f"SST должен быть между {MIN_SST_VALUE} и {MAX_SST_VALUE}")
                
            if 'sd' in slice_item and slice_item['sd']:
                validate_hex_value(slice_item['sd'], 'SD', SD_LEN, SD_LEN)
                
            if 'session' not in slice_item or not slice_item['session']:
                raise ValidationError("Каждый срез должен иметь хотя бы одну сессию")
                
            for session in slice_item['session']:
                validate_session(session)
                
        return slice_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Инициализация значений для существующего экземпляра
        if self.instance and hasattr(self.instance, 'pk') and self.instance.pk:
            self._init_existing_instance()

    def _init_existing_instance(self):
        """Инициализация данных для существующего абонента"""
        self.fields['msisdn'].initial = getattr(self.instance, 'msisdn', [])
        
        # Инициализация security
        security = getattr(self.instance, 'security', {})
        if isinstance(security, dict):
            self.fields['security'].initial = security
        else:
            self.fields['security'].initial = {
                'k': security.k,
                'amf': security.amf,
                'op': security.op,
                'opc': security.opc,
                'sqn': security.sqn
            }
        
        # Инициализация ambr
        ambr = getattr(self.instance, 'ambr', {})
        if isinstance(ambr, dict):
            self.fields['ambr'].initial = ambr
        else:
            self.fields['ambr'].initial = {
                'downlink': {
                    'value': ambr.downlink.value,
                    'unit': self._get_choice_display(ambr.downlink.unit, UNIT_CHOICES)
                },
                'uplink': {
                    'value': ambr.uplink.value,
                    'unit': self._get_choice_display(ambr.uplink.unit, UNIT_CHOICES)
                }
            }
        
        # Инициализация срезов
        slices = getattr(self.instance, 'slice', [])
        slices_data = []
        for slice_obj in slices:
            if isinstance(slice_obj, dict):
                slice_data = slice_obj
            else:
                slice_data = {
                    'sst': slice_obj.sst,
                    'default_indicator': slice_obj.default_indicator,
                    'sd': slice_obj.sd,
                    'session': []
                }

                for session_obj in slice_obj.session:
                    session_data = self._prepare_session_data(session_obj)
                    slice_data['session'].append(session_data)
            
            slices_data.append(slice_data)
        
        self.fields['slice'].initial = slices_data

    def _get_choice_display(self, value, choices):
        """Получает отображаемое значение для choice по значению"""
        for choice in choices:
            if choice[0] == value:
                return choice[1]
        return value

    def _prepare_session_data(self, session_obj):
        """Подготовка данных сессии для инициализации формы"""
        if isinstance(session_obj, dict):
            return session_obj
            
        return {
            'name': session_obj.name,
            'type': self._get_choice_display(session_obj.type, SESSION_TYPE_CHOICES),
            'qos': {
                'index': session_obj.qos.index,
                'arp': {
                    'priority_level': session_obj.qos.arp.priority_level,
                    'pre_emption_capability': self._get_choice_display(
                        session_obj.qos.arp.pre_emption_capability, EMPTION_CHOICES
                    ),
                    'pre_emption_vulnerability': self._get_choice_display(
                        session_obj.qos.arp.pre_emption_vulnerability, EMPTION_CHOICES
                    )
                },
                'mbr': {
                    'downlink': {
                        'value': session_obj.qos.mbr.downlink.value,
                        'unit': self._get_choice_display(
                            session_obj.qos.mbr.downlink.unit, UNIT_CHOICES
                        )
                    },
                    'uplink': {
                        'value': session_obj.qos.mbr.uplink.value,
                        'unit': self._get_choice_display(
                            session_obj.qos.mbr.uplink.unit, UNIT_CHOICES
                        )
                    }
                },
                'gbr': {
                    'downlink': {
                        'value': session_obj.qos.gbr.downlink.value,
                        'unit': self._get_choice_display(
                            session_obj.qos.gbr.downlink.unit, UNIT_CHOICES
                        )
                    },
                    'uplink': {
                        'value': session_obj.qos.gbr.uplink.value,
                        'unit': self._get_choice_display(
                            session_obj.qos.gbr.uplink.unit, UNIT_CHOICES
                        )
                    }
                }
            },
            'ambr': {
                'downlink': {
                    'value': session_obj.ambr.downlink.value,
                    'unit': self._get_choice_display(
                        session_obj.ambr.downlink.unit, UNIT_CHOICES
                    )
                },
                'uplink': {
                    'value': session_obj.ambr.uplink.value,
                    'unit': self._get_choice_display(
                        session_obj.ambr.uplink.unit, UNIT_CHOICES
                    )
                }
            },
            'pcc_rule': [
                {
                    'qos': {
                        'index': pcc_rule.qos.index,
                        'arp': {
                            'priority_level': pcc_rule.qos.arp.priority_level,
                            'pre_emption_capability': self._get_choice_display(
                                pcc_rule.qos.arp.pre_emption_capability, EMPTION_CHOICES
                            ),
                            'pre_emption_vulnerability': self._get_choice_display(
                                pcc_rule.qos.arp.pre_emption_vulnerability, EMPTION_CHOICES
                            )
                        },
                        'mbr': {
                            'downlink': {
                                'value': pcc_rule.qos.mbr.downlink.value,
                                'unit': self._get_choice_display(
                                    pcc_rule.qos.mbr.downlink.unit, UNIT_CHOICES
                                )
                            },
                            'uplink': {
                                'value': pcc_rule.qos.mbr.uplink.value,
                                'unit': self._get_choice_display(
                                    pcc_rule.qos.mbr.uplink.unit, UNIT_CHOICES
                                )
                            }
                        },
                        'gbr': {
                            'downlink': {
                                'value': pcc_rule.qos.gbr.downlink.value,
                                'unit': self._get_choice_display(
                                    pcc_rule.qos.gbr.downlink.unit, UNIT_CHOICES
                                )
                            },
                            'uplink': {
                                'value': pcc_rule.qos.gbr.uplink.value,
                                'unit': self._get_choice_display(
                                    pcc_rule.qos.gbr.uplink.unit, UNIT_CHOICES
                                )
                            }
                        }
                    },
                    'flow': getattr(pcc_rule, 'flow', [])
                }
                for pcc_rule in getattr(session_obj, 'pcc_rule', [])
            ]
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Обработка security
        security_data = self.cleaned_data['security']
        if isinstance(instance.security, dict):
            instance.security = Security(**security_data)
        else:
            instance.security.k = security_data['k']
            instance.security.amf = security_data['amf']
            instance.security.op = security_data.get('op')
            instance.security.opc = security_data.get('opc')
            instance.security.sqn = security_data.get('sqn')
        
        # Обработка ambr
        ambr_data = self.cleaned_data['ambr']
        if isinstance(instance.ambr, dict):
            instance.ambr = Ambr(
                downlink=AmbrLink(
                    value=ambr_data['downlink']['value'],
                    unit=ambr_data['downlink']['unit']
                ),
                uplink=AmbrLink(
                    value=ambr_data['uplink']['value'],
                    unit=ambr_data['uplink']['unit']
                )
            )
        else:
            instance.ambr.downlink.value = ambr_data['downlink']['value']
            instance.ambr.downlink.unit = ambr_data['downlink']['unit']
            instance.ambr.uplink.value = ambr_data['uplink']['value']
            instance.ambr.uplink.unit = ambr_data['uplink']['unit']
        
        # Обработка срезов
        slices = []
        for slice_item in self.cleaned_data['slice']:
            if isinstance(slice_item, dict):
                slice_obj = Slice(**slice_item)
            else:
                slice_obj = slice_item
            
            # Обработка сессий
            sessions = []
            for session_item in slice_item['session']:
                if isinstance(session_item, dict):
                    session_obj = Session(**session_item)
                else:
                    session_obj = session_item
                
                sessions.append(session_obj)
            
            slice_obj.session = sessions
            slices.append(slice_obj)
        
        instance.slice = slices
        instance.msisdn = self.cleaned_data['msisdn']
        
        if commit:
            instance.save()
            
        return instance
