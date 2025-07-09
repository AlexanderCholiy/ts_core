from django import forms
from django_jsonform.widgets import JSONFormWidget

from .constants import MAX_SUBSCRIBER_IMSI_LEN, MAX_SUBSCRIBER_MSISDN_LEN
from .models import Subscriber


class SubscriberForm(forms.ModelForm):

    class Meta:
        model = Subscriber
        fields = ('imsi', 'msisdn')
        widgets = {
            'imsi': forms.TextInput(attrs={
                'pattern': '\\d+',
                'maxlength': MAX_SUBSCRIBER_IMSI_LEN,
            }),
            'msisdn': JSONFormWidget(schema={
                    'type': 'array',
                    'items': {
                        'type': 'string',
                        'pattern': '^\\d+$',
                        'maxLength': MAX_SUBSCRIBER_MSISDN_LEN,
                    },
                    'minItems': 0,
                    'uniqueItems': True,
            }),
        }
