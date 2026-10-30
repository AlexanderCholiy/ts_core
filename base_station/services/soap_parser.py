from xml.etree import ElementTree

from base_station.constants import SOAP_NAMESPACE, NS_MAP
from base_station.services.soap_request_schemas import SoapEnvelope
from base_station.services.soap_transfer_schemas import (
    AutonomousTransferComplete,
)
from typing import Optional


def parse_soap_envelope(xml: bytes) -> SoapEnvelope:
    """Разбирает XML с идентификаторами базовой станции."""
    return SoapEnvelope.from_xml(xml)


def is_soap_fault(xml_data: bytes) -> bool:
    """Проверяет, содержит ли SOAP Envelope сообщение Fault."""
    if not xml_data or not xml_data.strip():
        return False

    try:
        root = ElementTree.fromstring(xml_data)
    except ElementTree.ParseError:
        raise

    body = root.find(f'{{{SOAP_NAMESPACE}}}Body')

    return (
        body is not None
        and body.find(f'{{{SOAP_NAMESPACE}}}Fault') is not None
    )


def get_soap_method(xml_data: bytes) -> Optional[str]:
    """Возвращает название RPC-метода из SOAP Body."""
    root = ElementTree.fromstring(xml_data)

    body = root.find(f'{{{SOAP_NAMESPACE}}}Body')

    if body is None or not len(body):
        return None

    tag = body[0].tag

    return tag.split('}', 1)[-1] if '}' in tag else tag


def parse_autonomous_transfer_complete(
    xml: bytes,
) -> AutonomousTransferComplete:
    """Разбирает RPC AutonomousTransferComplete из SOAP Envelope."""
    root = ElementTree.fromstring(xml)

    body = root.find(f'{{{SOAP_NAMESPACE}}}Body')

    if body is None:
        raise ValueError('В SOAP Envelope отсутствует Body.')

    cwmp_namespace = NS_MAP['cwmp']
    rpc = body.find(
        f'{{{cwmp_namespace}}}AutonomousTransferComplete'
    )

    if rpc is None:
        raise ValueError(
            'В SOAP Body отсутствует AutonomousTransferComplete.'
        )

    rpc_xml = ElementTree.tostring(rpc, encoding='utf-8')

    return AutonomousTransferComplete.from_xml(rpc_xml)


def get_soap_message_id(xml_data: bytes) -> Optional[str]:
    """Возвращает идентификатор сообщения из SOAP Header."""
    root = ElementTree.fromstring(xml_data)

    header = root.find(f'{{{SOAP_NAMESPACE}}}Header')

    if header is None:
        return None

    cwmp_namespace = NS_MAP['cwmp']

    message_id = header.find(
        f'{{{cwmp_namespace}}}ID'
    )

    return (
        message_id.text
        if message_id is not None and message_id.text
        else None
    )
