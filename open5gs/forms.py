from bson import ObjectId
from django import forms
from django.core.exceptions import ValidationError
from django_jsonform.widgets import JSONFormWidget

from .constants import (
    MAX_SST_VALUE,
    MAX_SUBSCRIBER_HEX_LEN,
    MAX_SUBSCRIBER_MSISDN_LEN,
    MIN_SST_VALUE,
    SD_LEN,
)
from .models import Subscriber
from .schemas import AMBR_SCHEMA, MSISDN_SCHEMA, SECURITY_SCHEMA, SLICE_SCHEMA
from .utils import MongoJSONEncoder
from .validators import (
    is_valid_objectid,
    validate_br,
    validate_hex_value,
    validate_session,
)


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
                # Оставляем только непустые значения:
                for field in ['ue', 'smf']:
                    ip_config = session.get(field)

                    if ip_config:
                        ip_config = {k: v for k, v in ip_config.items() if v}
                        if ip_config:
                            session[field] = ip_config
                        else:
                            session.pop(field, None)

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

        hex_fields = ['k', 'amf', 'op', 'opc']
        cleaned_security = {}
        for field, value in security_data.items():
            if field in hex_fields and value and isinstance(value, str):
                cleaned_security[field] = value.replace(' ', '')
            else:
                cleaned_security[field] = value

        if not all(k in cleaned_security for k in ['k', 'amf']):
            raise ValidationError(
                'Поля "Subscriber Key (K)" и '
                '"Authentication Management Field (AMF)" обязательны'
            )

        for field, name in [
            ('k', 'Subscriber Key (K)'),
            ('amf', 'Authentication Management Field (AMF)'),
            ('op', 'Operator Key (OP)'),
            ('opc', 'Operator Key (OPc)'),
        ]:
            if field in cleaned_security and cleaned_security[field]:
                validate_hex_value(
                    cleaned_security[field], name, MAX_SUBSCRIBER_HEX_LEN)

        if cleaned_security.get('op') and cleaned_security.get('opc'):
            raise ValidationError('Укажите только OP или OPc')

        # Замена на None пустых значений
        if not cleaned_security.get('op'):
            cleaned_security['op'] = None
        if not cleaned_security.get('opc'):
            cleaned_security['opc'] = None

        return cleaned_security

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
        self.fields['msisdn'].initial = getattr(self.instance, 'msisdn', [])
        self.fields['ambr'].initial = getattr(self.instance, 'ambr', {})
        self.fields['slice'].initial = getattr(self.instance, 'slice', [])

        # Обработка security полей с удалением пробелов
        security_data = getattr(self.instance, 'security', {})
        if security_data:
            cleaned_security = {}
            hex_fields = ['k', 'amf', 'op', 'opc']

            for field, value in security_data.items():
                if field in hex_fields and value and isinstance(value, str):
                    cleaned_security[field] = value.replace(' ', '')
                else:
                    cleaned_security[field] = value

            self.fields['security'].initial = cleaned_security
        else:
            self.fields['security'].initial = {}

    def save(self, commit=True):
        instance: Subscriber = super().save(commit=False)

        # Новые JSON данные из формы:
        new_msisdn: list[str] = self.cleaned_data.get('msisdn', [])
        new_security: dict = self.cleaned_data.get('security', {})
        new_ambr: dict = self.cleaned_data.get('ambr', {})
        new_slice: list[dict] = self.cleaned_data.get('slice', [])

        # MSISDN и Ambr не имеют доп. полей:
        instance.msisdn = new_msisdn
        instance.ambr = new_ambr
        # Slice имеет скрытые поля _id, flow которые надо проверить:
        instance.slice = self.add_hide_objects_to_slice(new_slice)

        # Security имеет скрытое поле sqn (sqn: Long('2529')):
        if instance.pk:
            old_sqn = getattr(instance, 'security', {}).get('sqn')
        else:
            old_sqn = None

        security = new_security.copy()
        security['sqn'] = old_sqn
        instance.security = security

        if commit:
            instance.save()

        return instance

    @staticmethod
    def add_hide_objects_to_slice(slices: list[dict]) -> list[dict]:
        """Добавлям скрытые поля, которые должны быть по умолчанию"""
        for slice_item in slices:
            used_ids = set()

            def get_unique_objectid():
                new_id = ObjectId()
                while str(new_id) in used_ids:
                    new_id = ObjectId()
                used_ids.add(str(new_id))
                return new_id

            if not is_valid_objectid(slice_item.get('_id')):
                slice_item['_id'] = get_unique_objectid()
            else:
                oid_str = str(slice_item['_id'])
                if oid_str in used_ids:
                    slice_item['_id'] = get_unique_objectid()
                else:
                    used_ids.add(oid_str)

            for session in slice_item.get('session', []):
                if not is_valid_objectid(session.get('_id')):
                    session['_id'] = get_unique_objectid()
                else:
                    oid_str = str(session['_id'])
                    if oid_str in used_ids:
                        session['_id'] = get_unique_objectid()
                    else:
                        used_ids.add(oid_str)

                for pcc_rule in session.get('pcc_rule', []):
                    if not is_valid_objectid(pcc_rule.get('_id')):
                        pcc_rule['_id'] = get_unique_objectid()
                    else:
                        oid_str = str(pcc_rule['_id'])
                        if oid_str in used_ids:
                            pcc_rule['_id'] = get_unique_objectid()
                        else:
                            used_ids.add(oid_str)

                    if (
                        'flow' not in pcc_rule
                        or not isinstance(pcc_rule['flow'], list)
                    ):
                        pcc_rule['flow'] = []

        return slices
