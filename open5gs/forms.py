from django import forms

from .models import Subscriber
from .constants import MAX_SUBSCRIBER_MSISDN_LEN


class MSISDNWidget(forms.widgets.TextInput):
    def render(self, name, value, attrs=None, renderer=None):
        if isinstance(value, list):
            value = ', '.join(value)
        return super().render(name, value, attrs, renderer)


class SubscriberForm(forms.ModelForm):
    # msisdn
    msisdn = forms.CharField(
        label='MSISDN',
        required=False,
        widget=MSISDNWidget(attrs={'class': 'vTextField'}),
        help_text=(
            'Введите номера через запятую. '
            f'Каждый номер — только цифры, до {MAX_SUBSCRIBER_MSISDN_LEN} '
            'символов.'
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
        fields = ('imsi', 'msisdn', 'security', 'ambr')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.msisdn:
            self.fields['msisdn'].initial = ', '.join(self.instance.msisdn)

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
        msisdn_raw: str = self.cleaned_data.get('msisdn', '')
        if not msisdn_raw.strip():
            return []

        numbers = []
        for part in msisdn_raw.split(','):
            num = part.strip()
            if num:
                if not num.isdigit():
                    raise forms.ValidationError(
                        f'Номер "{num}" должен содержать только цифры.')
                if len(num) > MAX_SUBSCRIBER_MSISDN_LEN:
                    raise forms.ValidationError(
                        f'Номер "{num}" не должен быть длиннее '
                        f'{MAX_SUBSCRIBER_MSISDN_LEN} символов.'
                    )
                numbers.append(num)

        if len(numbers) != len(set(numbers)):
            raise forms.ValidationError(
                'Номера MSISDN должны быть уникальными.')

        return numbers

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
