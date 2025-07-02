from django.db import models

from .constants import (
    MAX_STATUS_DESCRIPTION_LEN,
    MAX_POLE_ADRESS_LEN,
    MAX_POLE_LEN,
    MAX_OPERATOR_NAME_LEN,
    MAX_OPERATOR_ST_NAME_LEN,
    MAX_MODEM_IP_LEN,
    MAX_MODEM_PHONE_LEN,
    MAX_MODEM_MAC_LEN,
    MAX_MODEM_SERIAL_LEN,
    MAX_MODEM_IMSI_LEN,
    MAX_MODEM_VERSION_LEN,
    MAX_MODEM_LATITUDE_LEN,
    MAX_MODEM_LONGTITUDE_LEN,
    MAX_MODEM_FIRMWARE_LEN,
    MAX_MODEM_CABINET_LEN,
    MAX_MODEM_COUNTER_LEN,
    DEFAULT_POLE_ID,
)


class Pole(models.Model):
    id = models.CharField(
        'Шифр опоры',
        primary_key=True,
        max_length=MAX_POLE_LEN,
        db_column='PoleID',
    )
    status = models.ForeignKey(
        'Status',
        on_delete=models.DO_NOTHING,
        db_column='PoleStatus',
        verbose_name='Статус',
        related_name='pole_statuses',
    )
    address = models.CharField(
        'Адрес',
        max_length=MAX_POLE_ADRESS_LEN,
        null=True,
        blank=True,
        db_column='PoleAddress',
    )
    latitude = models.FloatField(
        'Широта',
        null=True,
        blank=True,
        db_column='PoleLatitude',
    )
    longitude = models.FloatField(
        'Долгота',
        null=True,
        blank=True,
        db_column='PoleLongtitude',
    )
    master = models.CharField(
        'Мастер опора',
        max_length=MAX_POLE_LEN,
        null=True,
        blank=True,
        db_column='PoleMaster',
    )
    on_air_date = models.DateField(
        'Дата включения',
        null=True,
        blank=True,
        db_column='PoleOnAirDate',
    )
    operator_1 = models.ForeignKey(
        'Operator',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='PoleOp1',
        verbose_name='Первый оператор',
        related_name='pole_operators_1',
    )
    operator_2 = models.ForeignKey(
        'Operator',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='PoleOp2',
        verbose_name='Второй оператор',
        related_name='pole_operators_2',
    )
    operator_3 = models.ForeignKey(
        'Operator',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='PoleOp3',
        verbose_name='Третий оператор',
        related_name='pole_operators_3',
    )
    contractor = models.ForeignKey(
        'Operator',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='PoleContr',
        verbose_name='Подрядчик',
        related_name='pole_contractors',
    )

    class Meta:
        app_label = 'monitoring'
        db_table = 'Msys_Poles'
        managed = False
        verbose_name = 'опора'
        verbose_name_plural = 'Опоры'

    def __str__(self):
        return self.id


class Status(models.Model):
    id = models.AutoField(primary_key=True, db_column='StatusID')
    description = models.CharField(
        'Описание',
        max_length=MAX_STATUS_DESCRIPTION_LEN,
        null=True,
        blank=True,
        db_column='StatusDesc',
    )

    class Meta:
        app_label = 'monitoring'
        db_table = 'MSys_Statuses'
        managed = False
        verbose_name = 'статус'
        verbose_name_plural = 'Статусы'

    def __str__(self):
        return f'{self.id}: {self.description}'


class Operator(models.Model):
    id = models.AutoField(primary_key=True, db_column='OrgID')
    name = models.CharField(
        'Название',
        max_length=MAX_OPERATOR_NAME_LEN,
        null=True,
        blank=True,
        db_column='OrgName',
    )
    st_name = models.CharField(
        'Аббревиатура',
        max_length=MAX_OPERATOR_ST_NAME_LEN,
        null=True,
        blank=True,
        db_column='OrgShort',
    )

    class Meta:
        app_label = 'monitoring'
        db_table = 'Msys_Orgs'
        managed = False
        verbose_name = 'оператор'
        verbose_name_plural = 'Операторы'

    def __str__(self):
        return self.name or f'undefined {self.id}'


class Modem(models.Model):
    id = models.CharField(
        'IP модема',
        primary_key=True,
        max_length=MAX_MODEM_IP_LEN,
        db_column='ModemID',
    )
    level = models.IntegerField(
        'Тип устройсва',
        db_column='ModemLevel',
    )
    status = models.ForeignKey(
        Status,
        on_delete=models.DO_NOTHING,
        db_column='ModemStatus',
        verbose_name='Статус',
        related_name='modem_statuses',
    )
    pole_1 = models.ForeignKey(
        Pole,
        on_delete=models.SET(
            lambda: Pole.objects.get(id=DEFAULT_POLE_ID)),
        db_column='ModemPole',
        verbose_name='Первая опора',
        related_name='modem_poles_1',
    )
    pole_2 = models.ForeignKey(
        Pole,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='ModemPole2',
        verbose_name='Вторая опора',
        related_name='modem_poles_2',
    )
    pole_3 = models.ForeignKey(
        Pole,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='ModemPole3',
        verbose_name='Третья опора',
        related_name='modem_poles_3',
    )
    phone = models.CharField(
        'Телефон',
        max_length=MAX_MODEM_PHONE_LEN,
        null=True,
        blank=True,
        db_column='ModemMsisdn',
    )
    status_timestamp = models.DateTimeField(
        'Время изменения статуса',
        null=True,
        blank=True,
        db_column='ModemAlarmtimestamp',
    )
    mac = models.CharField(
        'MAC-адрес',
        max_length=MAX_MODEM_MAC_LEN,
        null=True,
        blank=True,
        db_column='ModemCounter',
    )
    serial = models.CharField(
        'Серийный номер',
        max_length=MAX_MODEM_SERIAL_LEN,
        null=True,
        blank=True,
        db_column='ModemSerial',
    )
    imsi = models.CharField(
        'серийный номер sim карты',
        max_length=MAX_MODEM_IMSI_LEN,
        null=True,
        blank=True,
        db_column='ModemIMSI',
    )
    version = models.CharField(
        'Версия контроллера',
        max_length=MAX_MODEM_VERSION_LEN,
        null=True,
        blank=True,
        db_column='ModemVersion',
    )
    latitude = models.CharField(
        'Широта',
        max_length=MAX_MODEM_LATITUDE_LEN,
        null=True,
        blank=True,
        db_column='ModemLatitude',
    )
    longtitude = models.CharField(
        'Долгота',
        max_length=MAX_MODEM_LONGTITUDE_LEN,
        null=True,
        blank=True,
        db_column='ModemLongtitude',
    )
    firmware = models.CharField(
        'Прошивка',
        max_length=MAX_MODEM_FIRMWARE_LEN,
        null=True,
        blank=True,
        db_column='ModemFirmware',
    )
    watchdog = models.IntegerField(
        'датчик двери',
        null=True,
        blank=True,
        db_column='ModemWatchdog',
    )
    cabinet_serial = models.CharField(
        'Серийный номер шкафа',
        max_length=MAX_MODEM_CABINET_LEN,
        null=True,
        blank=True,
        db_column='ModemCabinetSerial',
    )

    class Meta:
        app_label = 'monitoring'
        db_table = 'MSys_Modems'
        managed = False
        verbose_name = 'модем'
        verbose_name_plural = 'Модемы'

    def __str__(self):
        return self.id


class Counter(models.Model):
    id = models.CharField(
        'Номер счетчика',
        primary_key=True,
        max_length=MAX_MODEM_COUNTER_LEN,
        db_column='CounterID',
    )
    modem = models.ForeignKey(
        Modem,
        on_delete=models.DO_NOTHING,
        db_column='CounterModem',
        verbose_name='Модем',
        related_name='counter_modems',
    )
    status = models.ForeignKey(
        Status,
        on_delete=models.DO_NOTHING,
        db_column='CounterStatus',
        verbose_name='Статус',
        related_name='counter_statuses',
    )
    number = models.PositiveIntegerField(
        'Порядковый номер',
        null=True,
        blank=True,
        db_column='CounterNumber'
    )
    operator = models.ForeignKey(
        Operator,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='CounterOp',
        verbose_name='Оператор',
        related_name='counter_operators'
    )

    class Meta:
        app_label = 'monitoring'
        db_table = 'MSys_Counters'
        managed = False
        verbose_name = 'счётчик'
        verbose_name_plural = 'Счётчики'

    def __str__(self):
        return self.id
