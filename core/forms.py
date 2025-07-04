from django import forms

from core.models import Security


class SecurityForm(forms.ModelForm):

    class Meta:
        model = Security
        fields = ('k', 'amf', 'op', 'opc', 'sqn')
        widgets = {
            'k': forms.TextInput(attrs={
                'pattern': '[0-9A-Fa-f]+',
                'title': 'Только hex-символы (0-9, A-F)'
            }),
            'amf': forms.TextInput(attrs={
                'pattern': '[0-9A-Fa-f]+',
                'title': 'Только hex-символы (0-9, A-F)'
            }),
            'op': forms.TextInput(attrs={
                'pattern': '[0-9A-Fa-f]*',
                'title': 'Только hex-символы (0-9, A-F)'
            }),
            'opc': forms.TextInput(attrs={
                'pattern': '[0-9A-Fa-f]*',
                'title': 'Только hex-символы (0-9, A-F)'
            }),
            'sqn': forms.NumberInput(),
        }
