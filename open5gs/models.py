from djongo import models

from core.models import Security
from core.validators import digits_validator
from core.forms import SecurityForm
from .constants import MAX_SUBSCRIBER_IMSI_LEN


class Subscriber(models.Model):
    _id = models.ObjectIdField()
    imsi = models.CharField(
        'IMSI',
        max_length=MAX_SUBSCRIBER_IMSI_LEN,
        unique=True,
        help_text='Разрешены только цифры',
        validators=[digits_validator]
    )
    security = models.EmbeddedField(
        model_container=Security, model_form_class=SecurityForm
    )


    # ambr = models.JSONField(default=dict)
    # schema_version = models.IntegerField(default=1)
    # msisdn = models.JSONField(default=list)
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
