from djongo import models
from django.core.exceptions import ValidationError

from .constants import MAX_SUBSCRIBER_HEX_LEN
from .validators import hexadecimal_validator


class Security(models.Model):
    k = models.CharField(
        'Subscriber Key (K)',
        max_length=MAX_SUBSCRIBER_HEX_LEN,
        validators=[hexadecimal_validator]
    )
    amf = models.CharField(
        'Authentication Management Field (AMF)',
        max_length=MAX_SUBSCRIBER_HEX_LEN,
        validators=[hexadecimal_validator]
    )
    op = models.CharField(
        'USIM Type: OP',
        max_length=MAX_SUBSCRIBER_HEX_LEN,
        null=True,
        blank=True,
        validators=[hexadecimal_validator]
    )
    opc = models.CharField(
        'USIM Type: OPc',
        null=True,
        blank=True,
        max_length=MAX_SUBSCRIBER_HEX_LEN,
        validators=[hexadecimal_validator]
    )
    sqn = models.BigIntegerField(
        'Sequence Number',
        null=True,
        blank=True,
        help_text='Параметр в аутентификации 3G/4G/5G.'
    )

    class Meta:
        abstract = True

    def clean(self):
        if self.op is not None and self.opc is not None:
            raise ValidationError('Выберите либо OP, либо OPC.')
        if self.op is None and self.opc is None:
            raise ValidationError('Необходимо указать либо OP, либо OPc.')
