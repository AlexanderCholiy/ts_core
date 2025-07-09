from djongo import models
from django.core.exceptions import ValidationError
from django.core.validators import (
    MinValueValidator, MaxValueValidator, MinLengthValidator
)

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
from .forms import SessionForm


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
    sqn = models.PositiveBigIntegerField(
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


class AmbrLink(models.Model):
    value = models.PositiveIntegerField('Скорость передачи данных')
    unit = models.PositiveIntegerField(
        'Единица измерения скорости',
        choices=UNIT_CHOICES,
    )

    class Meta:
        abstract = True


class Ambr(models.Model):
    downlink = models.EmbeddedField(AmbrLink)
    uplink = models.EmbeddedField(AmbrLink)

    class Meta:
        abstract = True


class QosArp(models.Model):
    priority_level = models.PositiveSmallIntegerField(
        'ARP Priority Level',
        validators=[
            MinValueValidator(MIN_PRIORITY_LEVEL_VALUE),
            MaxValueValidator(MAX_PRIORITY_LEVEL_VALUE)
        ],
    )
    pre_emption_capability = models.PositiveSmallIntegerField(
        'Capability',
        choices=EMPTION_CHOICES,
    )
    pre_emption_vulnerability = models.PositiveSmallIntegerField(
        'Vulnerability',
        choices=EMPTION_CHOICES,
    )

    class Meta:
        abstract = True


class Qos(models.Model):
    arp = models.EmbeddedField(QosArp)
    mbr = models.EmbeddedField(Ambr)  # Session-AMBR Downlink
    gbr = models.EmbeddedField(Ambr)  # Session-AMBR Uplink
    index = models.PositiveSmallIntegerField(
        '5QI/QCI',
        choices=QOS_INDEX_CHOICES,
    )

    class Meta:
        abstract = True


class PccRule(models.Model):
    """PCC Rules"""
    _id = models.ObjectIdField()
    qos = models.EmbeddedField(
        Qos,
        null=True,
        blank=True
    )
    flow = models.JSONField(default=list, blank=True)

    class Meta:
        abstract = True


class Session(models.Model):
    """Session Configurations"""
    _id = models.ObjectIdField()
    qos = models.EmbeddedField(Qos)
    ambr = models.EmbeddedField(Ambr)
    name = models.CharField('DNN/APN', max_length=MAX_SESSION_NAME_LEN)
    type = models.PositiveSmallIntegerField(
        'Session Type',
        choices=SESSION_TYPE_CHOICES,
    )
    pcc_rule = models.ArrayField(
        PccRule,
        default=list,
        blank=True
    )

    class Meta:
        abstract = True


class Slice(models.Model):
    """Slice Configurations"""
    _id = models.ObjectIdField()
    sst = models.PositiveSmallIntegerField(
        'Slice/Service Type (SST)',
        validators=[
            MinValueValidator(MIN_SST_VALUE), MaxValueValidator(MAX_SST_VALUE)
        ],
    )
    default_indicator = models.BooleanField(
        'Default S-NSSAI',
        default=False,
        blank=True
    )
    sd = models.CharField(
        'Slice Differentiator (SD)',
        max_length=SD_LEN,
        null=True,
        blank=True,
        validators=[hexadecimal_validator, MinLengthValidator(SD_LEN)]
    )
    session = models.ArrayField(
        Session,
        SessionForm,
        default=list,
    )

    class Meta:
        abstract = True
