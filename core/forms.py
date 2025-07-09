from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator

from .constants import (
    MAX_SUBSCRIBER_HEX_LEN,
    MAX_SESSION_NAME_LEN,
    UNIT_CHOICES,
    EMPTION_CHOICES,
    QOS_INDEX_CHOICES,
    SESSION_TYPE_CHOICES,
    MIN_PRIORITY_LEVEL_VALUE,
    MAX_PRIORITY_LEVEL_VALUE,
    MIN_SST_VALUE,
    MAX_SST_VALUE,
    SD_LEN,
)
from .validators import hexadecimal_validator


class SecurityForm(forms.Form):
    k = forms.CharField(
        max_length=MAX_SUBSCRIBER_HEX_LEN,
        validators=[hexadecimal_validator],
        label='Subscriber Key (K)'
    )
    amf = forms.CharField(
        max_length=MAX_SUBSCRIBER_HEX_LEN,
        validators=[hexadecimal_validator],
        label='Authentication Management Field (AMF)'
    )
    op = forms.CharField(
        max_length=MAX_SUBSCRIBER_HEX_LEN,
        required=False,
        validators=[hexadecimal_validator],
        label='USIM Type: OP'
    )
    opc = forms.CharField(
        max_length=MAX_SUBSCRIBER_HEX_LEN,
        required=False,
        validators=[hexadecimal_validator],
        label='USIM Type: OPc'
    )
    sqn = forms.IntegerField(
        required=False,
        label='Sequence Number',
        help_text='Параметр в аутентификации 3G/4G/5G.'
    )

    def clean(self):
        cleaned_data = super().clean()
        op = cleaned_data.get('op')
        opc = cleaned_data.get('opc')

        if op and opc:
            raise ValidationError('Выберите либо OP, либо OPC.')
        if not op and not opc:
            raise ValidationError('Необходимо указать либо OP, либо OPc.')

        return cleaned_data


class AmbrLinkForm(forms.Form):
    value = forms.IntegerField(
        min_value=0,
        label='Скорость передачи данных'
    )
    unit = forms.ChoiceField(
        choices=UNIT_CHOICES,
        label='Единица измерения скорости'
    )


class AmbrForm(forms.Form):
    # downlink = forms.JSONField(
    #     label='Downlink',
    #     widget=forms.HiddenInput
    # )
    # uplink = forms.JSONField(
    #     label='Uplink',
    #     widget=forms.HiddenInput
    # )
    downlink = AmbrLinkForm()
    uplink = AmbrLinkForm()


class QosArpForm(forms.Form):
    priority_level = forms.IntegerField(
        min_value=MIN_PRIORITY_LEVEL_VALUE,
        max_value=MAX_PRIORITY_LEVEL_VALUE,
        label='ARP Priority Level'
    )
    pre_emption_capability = forms.ChoiceField(
        choices=EMPTION_CHOICES,
        label='Capability'
    )
    pre_emption_vulnerability = forms.ChoiceField(
        choices=EMPTION_CHOICES,
        label='Vulnerability'
    )


class QosForm(forms.Form):
    # arp = forms.JSONField(widget=forms.HiddenInput)
    # mbr = forms.JSONField(widget=forms.HiddenInput)
    # gbr = forms.JSONField(widget=forms.HiddenInput)
    arp = QosArpForm()
    mbr = AmbrForm()
    gbr = AmbrForm()
    index = forms.ChoiceField(
        choices=QOS_INDEX_CHOICES,
        label='5QI/QCI'
    )


class PccRuleForm(forms.Form):
    # qos = forms.JSONField(required=False, widget=forms.HiddenInput)
    qos = QosForm()


class SessionForm(forms.Form):
    # qos = forms.JSONField(widget=forms.HiddenInput)
    # ambr = forms.JSONField(widget=forms.HiddenInput)
    qos = QosForm()
    ambr = AmbrForm()
    name = forms.CharField(
        max_length=MAX_SESSION_NAME_LEN,
        label='DNN/APN'
    )
    type = forms.ChoiceField(
        choices=SESSION_TYPE_CHOICES,
        label='Session Type'
    )
    pcc_rule = forms.JSONField(required=False, widget=forms.HiddenInput)


class SliceForm(forms.Form):
    sst = forms.IntegerField(
        min_value=MIN_SST_VALUE,
        max_value=MAX_SST_VALUE,
        label='Slice/Service Type (SST)'
    )
    default_indicator = forms.BooleanField(
        required=False,
        label='Default S-NSSAI'
    )
    sd = forms.CharField(
        max_length=SD_LEN,
        required=False,
        validators=[hexadecimal_validator, MinLengthValidator(SD_LEN)],
        label='Slice Differentiator (SD)'
    )
    session = forms.JSONField(required=False, widget=forms.HiddenInput)
    # session = forms.MultipleChoiceField(
    #     choices=SessionForm(),
    #     required=False,
    #     widget=forms.SelectMultiple
    # )
