from djongo import models

from .constants import (
    MAX_SUBSCRIBER_IMSI_LEN,
    OPERATOR_DETERMINED_BARRING_CHOICES,
    SUBSCRIBER_STATUS_CHOICES
)
from .validators import digits_validator


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
    security = models.JSONField(
        default=dict,
        help_text='Настройка безопасности'
    )
    ambr = models.JSONField(
        default=dict,
        help_text='Настройки максимальной скорости передачи данных'
    )
    subscriber_status = models.PositiveSmallIntegerField(
        'Subscriber Status',
        default=0,
        choices=SUBSCRIBER_STATUS_CHOICES,
        help_text='Текущий статус абонента в сети',
    )
    operator_determined_barring = models.PositiveSmallIntegerField(
        'Operator Determined Barring',
        default=0,
        choices=OPERATOR_DETERMINED_BARRING_CHOICES,
        help_text='Типы блокировок, наложенных оператором',
    )
    slice = models.JSONField(
        default=list,
        help_text='Список сетевых срезов (Network Slices)'
    )

    class Meta:
        db_table = 'subscribers'
        managed = False
        verbose_name = 'абонент'
        verbose_name_plural = 'Абоненты'

    def __str__(self):
        return self.imsi
