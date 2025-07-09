from django import forms
from django_json_widget.widgets import JSONEditorWidget

from .models import Subscriber
from .constants import MAX_SUBSCRIBER_MSISDN_LEN


class SubscriberForm(forms.ModelForm):
    # msisdn
    msisdn = forms.JSONField(
        label='MSISDN',
        required=False,
        initial=list,
        widget=JSONEditorWidget(
            mode='code',
            options={
                'modes': ['code', 'view'],
                'mode': 'code',
                'search': True,
            },
            width='100%',
            height='auto'
        ),
        help_text=(
            f'Список номеров (максимум {MAX_SUBSCRIBER_MSISDN_LEN} цифр '
            'каждый)'
        )
    )

    # security
    security_k = forms.CharField(
        label='Subscriber Key (K)',
        required=True,
        widget=forms.TextInput(attrs={
            'pattern': '[0-9A-Fa-f]+',
            'title': 'Только hex-символы (0-9, A-F)'
        }),
        strip=True,
    )
    security_amf = forms.CharField(
        label='Authentication Management Field (AMF)',
        required=True,
        widget=forms.TextInput(attrs={
            'pattern': '[0-9A-Fa-f]+',
            'title': 'Только hex-символы (0-9, A-F)'
        }),
        strip=True,
    )
    security_op = forms.CharField(
        label='USIM Type: OP',
        required=False,
        widget=forms.TextInput(attrs={
            'pattern': '[0-9A-Fa-f]*',
            'title': 'Только hex-символы (0-9, A-F)'
        }),
        strip=True,
    )
    security_opc = forms.CharField(
        label='USIM Type: OPc',
        required=False,
        widget=forms.TextInput(attrs={
            'pattern': '[0-9A-Fa-f]*',
            'title': 'Только hex-символы (0-9, A-F)'
        }),
        strip=True,
    )
    security_sqn = forms.IntegerField(
        label='Sequence Number',
        required=False,
        min_value=0,
    )

    # ambr
    ambr_downlink_value = forms.IntegerField(
        label='UE-AMBR Downlink',
        required=True,
        min_value=0,
    )
    ambr_downlink_unit = forms.IntegerField(
        label='Unit',
        required=True,
        min_value=0,
    )
    ambr_uplink_value = forms.IntegerField(
        label='UE-AMBR Uplink',
        required=True,
        min_value=0,
    )
    ambr_uplink_unit = forms.IntegerField(
        label='Unit',
        required=True,
        min_value=0,
    )

    class Meta:
        model = Subscriber
        fields = (
            'imsi',
            'msisdn',
            'security',
            'ambr',
            'subscriber_status',
            'operator_determined_barring',
            'slice',
        )
        widgets = {
            'msisdn': JSONEditorWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.msisdn:
            self.initial['msisdn'] = self.instance.msisdn

        if self.instance and self.instance.security:
            self.fields['security_k'].initial = self.instance.security.get(
                'k')
            self.fields['security_amf'].initial = self.instance.security.get(
                'amf')
            self.fields['security_op'].initial = self.instance.security.get(
                'op')
            self.fields['security_opc'].initial = self.instance.security.get(
                'opc')
            self.fields['security_sqn'].initial = self.instance.security.get(
                'sqn')

        if self.instance and self.instance.ambr:
            self.fields['ambr_downlink_value'].initial = (
                self.instance.ambr.get('downlink', {}).get('value'))
            self.fields['ambr_downlink_unit'].initial = (
                self.instance.ambr.get('downlink', {}).get('unit'))
            self.fields['ambr_uplink_value'].initial = (
                self.instance.ambr.get('uplink', {}).get('value'))
            self.fields['ambr_uplink_unit'].initial = (
                self.instance.ambr.get('uplink', {}).get('unit'))

    def clean(self):
        cleaned_data = super().clean()

        op = cleaned_data.get('security_op')
        opc = cleaned_data.get('security_opc')

        if op and opc:
            raise forms.ValidationError('Выберите либо OP, либо OPC.')

        if not op and not opc:
            raise forms.ValidationError(
                'Необходимо указать либо OP, либо OPc.')

        return cleaned_data

    def clean_msisdn(self):
        msisdn_data = self.cleaned_data.get('msisdn')

        if not msisdn_data:
            return []

        if not isinstance(msisdn_data, list):
            raise forms.ValidationError("MSISDN должен быть массивом номеров")

        for num in msisdn_data:
            if not str(num).isdigit():
                raise forms.ValidationError(
                    f'Номер "{num}" должен содержать только цифры')
            if len(str(num)) > MAX_SUBSCRIBER_MSISDN_LEN:
                raise forms.ValidationError(
                    f'Номер "{num}" не должен быть длиннее '
                    f'{MAX_SUBSCRIBER_MSISDN_LEN} символов')

        if len(msisdn_data) != len(set(msisdn_data)):
            raise forms.ValidationError('Номера должны быть уникальными')

        return msisdn_data

    def save(self, commit=True):
        instance: Subscriber = super().save(commit=False)

        instance.msisdn = self.cleaned_data['msisdn']

        security_data = {
            'k': self.cleaned_data['security_k'],
            'amf': self.cleaned_data['security_amf'],
            'op': self.cleaned_data['security_op'],
            'opc': self.cleaned_data['security_opc'],
            'sqn': self.cleaned_data['security_sqn'],
        }
        instance.security = security_data

        ambr_data = {
            'downlink': {
                'value': self.cleaned_data['ambr_downlink_value'],
                'unit': self.cleaned_data['ambr_downlink_unit'],
            },
            'uplink': {
                'value': self.cleaned_data['ambr_uplink_value'],
                'unit': self.cleaned_data['ambr_uplink_unit'],
            }
        }
        instance.ambr = ambr_data

        if commit:
            instance.save()
        return instance
