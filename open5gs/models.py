from djongo import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from .constants import MAX_SUBSCRIBER_IMSI_LEN, MAX_SUBSCRIBER_MSISDN_LEN
from core.models import Security, Ambr, Slice
from core.validators import digits_validator


class Subscriber(models.Model):
    _id = models.ObjectIdField()
    imsi = models.CharField(
        'IMSI',
        max_length=MAX_SUBSCRIBER_IMSI_LEN,
        unique=True,
        help_text='Разрешены только цифры',
        validators=[digits_validator]
    )
    msisdn = models.JSONField(
        'MSISDN',
        default=list,
        blank=True,
        help_text='Список номеров MSISDN'
    )
    security = models.EmbeddedField(Security)
    ambr = models.EmbeddedField(Ambr)
    subscriber_status = models.PositiveSmallIntegerField(
        'Subscriber Status',
        default=0,
        choices=[  # Ограничиваем возможные значения через choices
            (0, 'SERVICE GRANTED'),
            (1, 'OPERATOR DETERMINED BARRING'),
        ],
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1),
        ],
        help_text='Текущий статус абонента в сети',
    )
    operator_determined_barring = models.PositiveSmallIntegerField(
        'Operator Determined Barring',
        default=0,
        choices=[
            (0, '(0) All Packet Oriented Services Barred'),
            (1, '(1) Roamer Access HPLMN-AP Barred'),
            (2, '(2) Roamer Access to VPLMN-AP Barred'),
            (3, '(3) Barring of all outgoing calls'),
            (4, '(4) Barring of all outgoing international calls'),
            (
                5,
                (
                    '(5) Barring of all outgoing international calls except '
                    'those directed to the home PLMN country'
                )
            ),
            (6, '(6) Barring of all outgoing inter-zonal calls'),
            (
                7, (
                    '(7) Barring of all outgoing inter-zonal calls except '
                    'those directed to the home PLMN country'
                )
            ),
            (
                8,
                (
                    '(8) Barring of all outgoing international calls except '
                    'those directed to the home PLMN country and Barring of '
                    'all outgoing inter-zonal calls'
                )
            ),
        ],
        validators=[
            MinValueValidator(0),
            MaxValueValidator(8),
        ],
        help_text='Типы блокировок, наложенных оператором',
    )
    slice = models.ArrayField(
        model_container=Slice,
        help_text='Список сетевых срезов (Network Slices)'
    )

    class Meta:
        db_table = 'subscribers'
        managed = False
        verbose_name = 'абонент'
        verbose_name_plural = 'Абоненты'

    def __str__(self):
        return self.imsi

    def clean(self):
        super().clean()
        msisdn = self.msisdn or []

        if not isinstance(msisdn, list):
            raise ValidationError({'msisdn': 'Должен быть список.'})

        if len(msisdn) != len(set(msisdn)):
            raise ValidationError(
                {'msisdn': 'Номера MSISDN должны быть уникальными.'})

        for number in msisdn:
            if not isinstance(number, str):
                raise ValidationError(
                    {'msisdn': 'Каждый элемент должен быть строкой.'})
            if not number.isdigit():
                raise ValidationError(
                    {
                        'msisdn': (
                            f'Номер "{number}" должен содержать только цифры.')
                    }
                )
            if len(number) > MAX_SUBSCRIBER_MSISDN_LEN:
                raise ValidationError(
                    {
                        'msisdn': (
                            f'Номер "{number}" не должен быть длиннее '
                            f'{MAX_SUBSCRIBER_MSISDN_LEN} символов.'
                        )
                    }
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
