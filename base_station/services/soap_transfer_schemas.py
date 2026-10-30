from typing import Optional

from pydantic_xml import BaseXmlModel, element

from base_station.constants import NS_MAP, RESPONSE_NS_MAP
from base_station.services.soap_response_schemas import SoapResponseHeader


class AutonomousTransferFaultStruct(
    BaseXmlModel,
    tag='FaultStruct',
    ns='',
):
    """Информация об ошибке передачи файла."""

    fault_code: int = element(
        tag='FaultCode',
        ns='',
        description='Код ошибки передачи файла.',
    )

    fault_string: str = element(
        tag='FaultString',
        ns='',
        description='Описание ошибки передачи файла.',
    )


class AutonomousTransferComplete(
    BaseXmlModel,
    tag='AutonomousTransferComplete',
    ns='cwmp',
    nsmap=NS_MAP,
):
    """Уведомление CPE о завершении автономной передачи файла."""

    announce_url: str = element(
        tag='AnnounceURL',
        ns='',
        description='URL объявления передачи файла.',
    )

    transfer_url: str = element(
        tag='TransferURL',
        ns='',
        description='URL передаваемого файла.',
    )

    is_download: str = element(
        tag='IsDownload',
        ns='',
        description='Признак загрузки файла.',
    )

    file_type: str = element(
        tag='FileType',
        ns='',
        description='Тип передаваемого файла.',
    )

    file_size: int = element(
        tag='FileSize',
        ns='',
        description='Размер передаваемого файла в байтах.',
    )

    target_file_name: str = element(
        tag='TargetFileName',
        ns='',
        description='Имя целевого файла.',
    )

    fault_struct: AutonomousTransferFaultStruct = element(
        tag='FaultStruct',
        ns='',
        description='Результат передачи файла.',
    )

    start_time: str = element(
        tag='StartTime',
        ns='',
        description='Время начала передачи файла.',
    )

    complete_time: str = element(
        tag='CompleteTime',
        ns='',
        description='Время завершения передачи файла.',
    )


class AutonomousTransferCompleteResponse(
    BaseXmlModel,
    tag='AutonomousTransferCompleteResponse',
    ns='cwmp',
):
    """Ответ ACS на RPC AutonomousTransferComplete."""
    pass


class SoapAutonomousTransferCompleteResponseBody(
    BaseXmlModel,
    tag='Body',
    ns='soap-env',
    nsmap=RESPONSE_NS_MAP,
):
    """Тело SOAP-сообщения с ответом AutonomousTransferComplete."""

    autonomous_transfer_complete_response: (
        AutonomousTransferCompleteResponse
    ) = element(
        tag='AutonomousTransferCompleteResponse',
        ns='cwmp',
    )


class SoapAutonomousTransferCompleteResponseEnvelope(
    BaseXmlModel,
    tag='Envelope',
    ns='soap-env',
    nsmap=RESPONSE_NS_MAP,
):
    """SOAP Envelope с ответом AutonomousTransferComplete."""

    header: Optional[SoapResponseHeader] = element(
        tag='Header',
        ns='soap-env',
        default=None,
    )

    body: SoapAutonomousTransferCompleteResponseBody = element(
        tag='Body',
        ns='soap-env',
    )
