
from typing import Optional

from pydantic_xml import BaseXmlModel, element
from pydantic_xml import attr
from pydantic_xml import BaseXmlModel, attr, element

from base_station.constants import RESPONSE_NS_MAP


class InformResponse(BaseXmlModel, tag='InformResponse', ns='cwmp'):
    """Ответ ACS на RPC Inform от базовой станции."""

    max_envelopes: int = element(
        tag='MaxEnvelopes',
        description=(
            'Максимальное количество SOAP-сообщений '
            'в одном HTTP-ответе.'
        ),
    )


class SoapInformResponseBody(
    BaseXmlModel,
    tag='Body',
    ns='soap-env',
    nsmap=RESPONSE_NS_MAP,
):
    """Тело SOAP-сообщения с ответом InformResponse."""

    inform_response: InformResponse = element(
        tag='InformResponse',
        ns='cwmp',
    )


class SoapResponseHeaderId(
    BaseXmlModel,
    tag='ID',
    ns='cwmp',
    nsmap=RESPONSE_NS_MAP,
):
    """Идентификатор SOAP-сообщения с обязательной обработкой."""

    value: str

    must_understand: str = attr(
        name='mustUnderstand',
        ns='soap-env',
        default='1',
    )


class SoapResponseHeader(
    BaseXmlModel,
    tag='Header',
    ns='soap-env',
    nsmap=RESPONSE_NS_MAP,
):
    """Служебный заголовок исходящего SOAP-сообщения."""

    message_id: SoapResponseHeaderId = element(
        tag='ID',
        ns='cwmp',
    )


class SoapInformResponseEnvelope(
    BaseXmlModel,
    tag='Envelope',
    ns='soap-env',
    nsmap=RESPONSE_NS_MAP,
):
    """SOAP Envelope с ответом InformResponse."""

    header: Optional[SoapResponseHeader] = element(
        tag='Header',
        ns='soap-env',
        default=None,
    )
    body: SoapInformResponseBody = element(
        tag='Body',
        ns='soap-env',
    )
