from http import HTTPStatus
from pprint import pprint
from typing import Optional

from django.http import HttpRequest, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from pydantic import ValidationError
from pydantic_xml.errors import ParsingError

from core.logger import base_station_logger, django_logger
from core.services import safe_parse_request_body
from axes.helpers import get_client_ip_address
from base_station.services import (
    InformResponse,
    SoapAutonomousTransferCompleteResponseBody,
    SoapAutonomousTransferCompleteResponseEnvelope,
    SoapInformResponseBody,
    SoapInformResponseEnvelope,
    SoapResponseHeader,
    SoapResponseHeaderId,
    AutonomousTransferCompleteResponse,
    get_soap_message_id,
    get_soap_method,
    is_soap_fault,
    parse_autonomous_transfer_complete,
    parse_soap_envelope,
)
from xml.etree import ElementTree


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(require_POST, name='dispatch')
# @method_decorator(
#     ratelimit(key='ip', rate='10/s', block=True), name='dispatch'
# )
class BaseStationMetricsView(View):
    """Эндпоинт приёма метрик базовой станции."""

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        ip_address: Optional[str] = request.META.get('REMOTE_ADDR')
        axes_ip_address = get_client_ip_address(request)

        if ip_address != axes_ip_address:
            django_logger.warning(
                'IP-адреса не совпадают: '
                f'REMOTE_ADDR={ip_address}, AXES={axes_ip_address}',
            )

        if not request.body.strip():
            base_station_logger.debug(
                f'Получен пустой SOAP POST: ip={ip_address}'
            )
            return HttpResponse(status=HTTPStatus.OK)

        body_preview = safe_parse_request_body(request, 4000)

        try:
            if is_soap_fault(request.body):
                # base_station_logger.debug(
                #     f'Получен SOAP Fault: ip={ip_address}',
                # )
                return HttpResponse(status=HTTPStatus.OK)

            method = get_soap_method(request.body)

            if method == 'Inform':
                envelope = parse_soap_envelope(request.body)

                if envelope.header is None:
                    base_station_logger.warning(
                        f'Отсутствует SOAP Header: ip={ip_address}'
                    )
                    return HttpResponse(status=HTTPStatus.BAD_REQUEST)

                message_id = envelope.header.message_id

                response = SoapInformResponseEnvelope(
                    header=SoapResponseHeader(
                        message_id=SoapResponseHeaderId(
                            value=message_id,
                        ),
                    ),
                    body=SoapInformResponseBody(
                        inform_response=InformResponse(
                            max_envelopes=1,
                        ),
                    ),
                )

                xml = response.to_xml(
                    encoding='UTF-8',
                    xml_declaration=True,
                )

                device = envelope.body.inform.device_id
                # pprint(envelope.model_dump(), sort_dicts=False)

                base_station_logger.info(
                    f'Получен Inform от базовой станции: '
                    f'ip={ip_address}, device_id={device}'
                )

            elif method == 'AutonomousTransferComplete':
                transfer = parse_autonomous_transfer_complete(
                    request.body
                )

                message_id = get_soap_message_id(request.body)

                if message_id is None:
                    base_station_logger.warning(
                        f'Отсутствует cwmp:ID в SOAP Header: '
                        f'method={method}, ip={ip_address}'
                    )
                    return HttpResponse(
                        status=HTTPStatus.BAD_REQUEST
                    )

                response = (
                    SoapAutonomousTransferCompleteResponseEnvelope(
                        header=SoapResponseHeader(
                            message_id=SoapResponseHeaderId(
                                value=message_id,
                            ),
                        ),
                        body=SoapAutonomousTransferCompleteResponseBody(
                            autonomous_transfer_complete_response=(
                                AutonomousTransferCompleteResponse()
                            ),
                        ),
                    )
                )

                xml = response.to_xml(
                    encoding='UTF-8',
                    xml_declaration=True,
                )

                transfer_data = transfer.model_dump()

                base_station_logger.info(
                    f'Получен AutonomousTransferComplete: '
                    f'ip={ip_address}, '
                    f'data={transfer_data}'
                )

            else:
                base_station_logger.warning(
                    f'Получен неподдерживаемый SOAP RPC: '
                    f'method={method}, ip={ip_address}'
                )
                return HttpResponse(status=HTTPStatus.OK)

        except (
            ValidationError,
            ParsingError,
            ElementTree.ParseError,
        ) as e:
            base_station_logger.warning(
                f'Ошибка разбора SOAP: ip={ip_address}:\n{e}\n'
                f'Тело запроса: {body_preview}'
            )
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            base_station_logger.exception(
                f'Непредвиденная ошибка: ip={ip_address}:\n{e}\n'
                f'Тело запроса: {body_preview}'
            )
            return HttpResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return HttpResponse(
            xml,
            content_type='text/xml; charset=utf-8',
            status=HTTPStatus.OK,
        )
