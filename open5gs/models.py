from djongo import models
from django.core.exceptions import ValidationError

from .constants import MAX_SUBSCRIBER_IMSI_LEN, MAX_SUBSCRIBER_MSISDN_LEN
from core.models import Security, Ambr
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

    # schema_version = models.IntegerField(default=1)
    # imeisv = models.JSONField(default=list)
    # mme_host = models.JSONField(default=list)
    # mme_realm = models.JSONField(default=list)
    # purge_flag = models.JSONField(default=list)
    # access_restriction_data = models.IntegerField()
    # subscriber_status = models.IntegerField()
    # operator_determined_barring = models.IntegerField()
    # network_access_mode = models.IntegerField()
    # subscribed_rau_tau_timer = models.IntegerField()
    # slice = models.JSONField(default=list)
    # _v = models.IntegerField(default=0, db_column='__v')
    # mme_timestamp = models.BigIntegerField()

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
