from django import forms

from .models import Subscriber


class SubscriberForm(forms.ModelForm):
    security_k = forms.CharField(
        label='Subscriber Key (K)',
        required=True,
        widget=forms.TextInput(attrs={
            'pattern': '[0-9A-Fa-f]+',
            'title': 'Только hex-символы (0-9, A-F)'
        })
    )
    security_amf = forms.CharField(
        label='Authentication Management Field (AMF)',
        required=True,
        widget=forms.TextInput(attrs={
            'pattern': '[0-9A-Fa-f]+',
            'title': 'Только hex-символы (0-9, A-F)'
        })
    )
    security_op = forms.CharField(
        label='USIM Type: OP',
        required=False,
        widget=forms.TextInput(attrs={
            'pattern': '[0-9A-Fa-f]*',
            'title': 'Только hex-символы (0-9, A-F)'
        })
    )
    security_opc = forms.CharField(
        label='USIM Type: OPc',
        required=False,
        widget=forms.TextInput(attrs={
            'pattern': '[0-9A-Fa-f]*',
            'title': 'Только hex-символы (0-9, A-F)'
        })
    )
    security_sqn = forms.IntegerField(
        label='Sequence Number',
        required=False
    )

    class Meta:
        model = Subscriber
        fields = ('imsi', 'security',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

    def save(self, commit=True):
        instance: Subscriber = super().save(commit=False)

        security_data = {
            'k': self.cleaned_data['security_k'],
            'amf': self.cleaned_data['security_amf'],
            'op': self.cleaned_data['security_op'],
            'opc': self.cleaned_data['security_opc'],
            'sqn': self.cleaned_data['security_sqn'],
        }

        instance.security = security_data

        if commit:
            instance.save()
        return instance
