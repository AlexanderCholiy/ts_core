from django import forms

from core.models import Security


class SecurityForm(forms.ModelForm):

    class Meta:
        model = Security
        fields = ('k', 'amf', 'op', 'opc', 'sqn')
