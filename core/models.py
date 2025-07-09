from djongo import models
from django.core.exceptions import ValidationError
from django.core.validators import (
    MinValueValidator, MaxValueValidator, MinLengthValidator
)

from .constants import MAX_SUBSCRIBER_HEX_LEN, MAX_SESSION_NAME
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
        choices=[
            (0, 'bps'),
            (1, 'Kbps'),
            (2, 'Mbps'),
            (3, 'Gbps'),
            (4, 'Tbps'),
        ],
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
        'ARP Priority Level (1-15)',
        validators=[MinValueValidator(1), MaxValueValidator(15)],
    )
    pre_emption_capability = models.PositiveSmallIntegerField(
        'Capability',
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        choices=[
            (0, 'Disabled'),
            (1, 'Enabled'),
        ],
    )
    pre_emption_vulnerability = models.PositiveSmallIntegerField(
        'Vulnerability',
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        choices=[
            (0, 'Disabled'),
            (1, 'Enabled'),
        ],
    )

    class Meta:
        abstract = True


class Qos(models.Model):
    arp = models.EmbeddedField(QosArp)
    mbr = models.EmbeddedField(Ambr)  # Session-AMBR Downlink
    gbr = models.EmbeddedField(Ambr)  # Session-AMBR Uplink
    index = models.PositiveSmallIntegerField(
        '5QI/QCI',
        choices=[
            (1, 0),
            (2, 1),
            (3, 1),
            (4, 1),
            (65, 1),
            (66, 1),
            (67, 1),
            (75, 1),
            (71, 1),
            (72, 1),
            (73, 1),
            (74, 1),
            (76, 1),
            (5, 1),
            (6, 1),
            (7, 1),
            (8, 1),
            (9, 1),
            (69, 1),
            (70, 1),
            (79, 1),
            (80, 1),
            (82, 1),
            (83, 1),
            (84, 1),
            (85, 1),
            (86, 1),
        ],
    )

    class Meta:
        abstract = True


class PccRule(models.Model):
    """PCC Rules"""
    qos = models.ArrayField(
        Qos,
        default=list,
        blank=True
    )

    class Meta:
        abstract = True


class Session(models.Model):
    """Session Configurations"""
    qos = models.EmbeddedField(Qos)
    ambr = models.EmbeddedField(Ambr)
    name = models.CharField('DNN/APN', max_length=MAX_SESSION_NAME)
    type = models.PositiveSmallIntegerField(
        'Session Type',
        choices=[
            (1, 'IPv4'),
            (2, 'IPv6'),
            (3, 'IPv4v6'),
        ],
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
    sst = models.PositiveSmallIntegerField(
        'Slice/Service Type (SST)',
        validators=[MinValueValidator(1), MaxValueValidator(4)],
    )
    default_indicator = models.BooleanField(
        'Default S-NSSAI',
        default=False,
        blank=True
    )
    sd = models.CharField(
        'Slice Differentiator (SD)',
        max_length=6,
        null=True,
        blank=True,
        validators=[hexadecimal_validator, MinLengthValidator(6)]
    )
    session = models.ArrayField(
        Session,
        default=list,
        blank=True
    )

    class Meta:
        abstract = True
