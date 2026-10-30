from xml.etree import ElementTree

from base_station.constants import SOAP_NAMESPACE
from base_station.services.soap_schemas import SoapEnvelope


def parse_soap_envelope(xml: bytes) -> SoapEnvelope:
    """Разбирает XML с идентификаторами базовой станции."""
    return SoapEnvelope.from_xml(xml)


def is_soap_fault(xml_data: bytes) -> bool:
    root = ElementTree.fromstring(xml_data)

    body = root.find(f'{{{SOAP_NAMESPACE}}}Body')

    return (
        body is not None
        and body.find(f'{{{SOAP_NAMESPACE}}}Fault') is not None
    )
