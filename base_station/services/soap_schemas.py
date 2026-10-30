from datetime import datetime
from typing import Any, List, Optional

from pydantic import field_validator, model_validator
from pydantic_xml import BaseXmlModel, element

from base_station.constants import (
    NS_MAP,
    PARAMETER_TYPES,
    BaseStationParameter,
    BaseStationParameterType
)
from core.services import normalize_optional_string, normalize_required_string


class DeviceId(BaseXmlModel, tag='DeviceId'):
    """Идентификационные данные базовой станции."""

    manufacturer: str = element(
        tag='Manufacturer',
        description='Производитель оборудования.',
    )
    oui: str = element(
        tag='OUI',
        description='Уникальный идентификатор производителя.',
    )
    product_class: str = element(
        tag='ProductClass',
        description='Модель или класс базовой станции.',
    )
    serial_number: str = element(
        tag='SerialNumber',
        description='Уникальный серийный номер базовой станции.',
    )

    @field_validator(
        'manufacturer',
        'oui',
        'product_class',
        'serial_number',
        mode='before',
    )
    @classmethod
    def normalize_strings(cls, value: Any) -> str:
        return normalize_required_string(value)


class EventStruct(BaseXmlModel, tag='EventStruct'):
    """Информация об отдельном событии базовой станции."""

    event_code: str = element(
        tag='EventCode',
        description='Код и название события, например BOOT или BOOTSTRAP.',
    )
    command_key: Optional[str] = element(
        tag='CommandKey',
        default=None,
        description='Идентификатор команды, связанной с событием.',
    )

    @field_validator('event_code', mode='before')
    @classmethod
    def normalize_event_code(cls, value: Any) -> str:
        return normalize_required_string(value)

    @field_validator('command_key', mode='before')
    @classmethod
    def normalize_command_key(cls, value: Any) -> Optional[str]:
        return normalize_optional_string(value)


class EventList(BaseXmlModel, tag='Event'):
    """Список событий, переданных базовой станцией."""

    events: List[EventStruct] = element(
        tag='EventStruct',
        description='Перечень событий текущей сессии.',
    )


class ParameterValueStruct(BaseXmlModel, tag='ParameterValueStruct'):
    """Значение отдельного параметра базовой станции."""

    name: str = element(
        tag='Name',
        description='Полный путь к параметру в дереве TR-069.',
    )
    value: Optional[str] = element(
        tag='Value',
        default=None,
        description='Текущее значение параметра.',
    )

    @field_validator('name', mode='before')
    @classmethod
    def normalize_name(cls, value: Any) -> str:
        return normalize_required_string(value)

    @field_validator('value', mode='before')
    @classmethod
    def normalize_value(cls, value: Any) -> Optional[str]:
        return normalize_optional_string(value)

    @model_validator(mode='after')
    def validate_parameter(self):
        try:
            parameter = BaseStationParameter(self.name)
        except ValueError:
            raise ValueError(
                f'Неизвестный параметр базовой станции: {self.name}'
            )

        parameter_type = PARAMETER_TYPES[parameter]

        if self.value is None:
            if parameter_type == BaseStationParameterType.OPTIONAL:
                return self

            raise ValueError(
                f'Параметр {self.name} не может быть пустым.'
            )

        if parameter_type != BaseStationParameterType.OPTIONAL:
            try:
                parameter_type.value.validate_python(self.value)
            except ValueError as error:
                raise ValueError(
                    f'Некорректное значение параметра {self.name}: '
                    f'{self.value!r}.'
                ) from error

        return self


class ParameterList(BaseXmlModel, tag='ParameterList'):
    """Список параметров и их значений, переданных базовой станцией."""

    parameters: List[ParameterValueStruct] = element(
        tag='ParameterValueStruct',
        description='Перечень параметров телеметрии базовой станции.',
    )


class Inform(BaseXmlModel, tag='Inform', ns='cwmp', nsmap=NS_MAP):
    """Сообщение с информацией о состоянии базовой станции."""

    device_id: DeviceId = element(
        ns='',
        description='Идентификационные данные оборудования.',
    )
    event: EventList = element(
        ns='',
        description='События, вызвавшие отправку сообщения.',
    )
    max_envelopes: int = element(
        tag='MaxEnvelopes',
        ns='',
        description=(
            'Максимальное количество SOAP-конвертов, '
            'которое базовая станция может обработать в одном сообщении.'
        ),
    )
    current_time: datetime = element(
        tag='CurrentTime',
        ns='',
        description='Текущие дата и время на базовой станции.',
    )
    retry_count: int = element(
        tag='RetryCount',
        ns='',
        description='Кол-во повторных попыток отправки текущего сообщения.',
    )
    parameter_list: ParameterList = element(
        ns='',
        description='Список параметров и текущих значений оборудования.',
    )


class SoapHeader(BaseXmlModel, tag='Header', ns='soap-env', nsmap=NS_MAP):
    """Служебная информация заголовка SOAP-сообщения."""

    message_id: str = element(
        tag='ID',
        ns='cwmp',
        description='Уникальный идентификатор SOAP-сообщения.',
    )
    session_timeout: Optional[int] = element(
        tag='SessionTimeout',
        ns='cwmp',
        default=None,
        description='Таймаут сессии управления в секундах.',
    )

    @field_validator('message_id', mode='before')
    @classmethod
    def normalize_message_id(cls, value: Any) -> str:
        return normalize_required_string(value)


class SoapBody(BaseXmlModel, tag='Body', ns='soap-env', nsmap=NS_MAP):
    """Основное содержимое SOAP-сообщения."""

    inform: Inform = element(
        description='Данные, переданные базовой станцией в сообщении Inform.',
    )


class SoapEnvelope(
    BaseXmlModel,
    tag='Envelope',
    ns='soap-env',
    nsmap=NS_MAP,
):
    """Корневой SOAP-конверт."""

    header: Optional[SoapHeader] = element(
        tag='Header',
        ns='soap-env',
        default=None,
        description='Служебный заголовок SOAP.',
    )
    body: SoapBody = element(
        tag='Body',
        ns='soap-env',
        description='Основное тело SOAP-сообщения.',
    )
