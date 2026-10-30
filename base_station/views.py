from http import HTTPStatus
from pprint import pprint
from typing import Optional

from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from pydantic import ValidationError
from pydantic_xml.errors import ParsingError

from base_station.services import is_soap_fault, parse_soap_envelope
from core.logger import base_station_logger
from core.services import safe_parse_request_body


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(require_POST, name='dispatch')
@method_decorator(
    ratelimit(key='ip', rate='300/m', block=True), name='dispatch'
)
class BaseStationMetricsView(View):
    """Эндпоинт приёма метрик базовой станции."""

    def post(self, request: HttpRequest, *args, **kwargs):
        ip_address: Optional[str] = request.META.get('REMOTE_ADDR')

        try:
            if is_soap_fault(request.body):
                # base_station_logger.debug(
                #     f'Получен SOAP Fault: ip={ip_address}',
                # )
                return JsonResponse({'status': 'ok'}, status=HTTPStatus.OK)

            envelope = parse_soap_envelope(request.body)
        except (ValidationError, ParsingError) as e:
            body_preview = safe_parse_request_body(request, 4000)
            base_station_logger.warning(
                f'Ошибка разбора SOAP: ip={ip_address}:\n{e}\n'
                f'Тело запроса: {body_preview}'
            )
            return JsonResponse(
                {'status': 'error', 'message': 'Invalid SOAP message'},
                status=HTTPStatus.BAD_REQUEST,
            )
        except Exception as e:
            base_station_logger.exception(
                f'Непредвиденная ошибка от ip={ip_address}: {e}'
            )
            return JsonResponse(
                {'status': 'error', 'message': 'Internal server error'},
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        # device = envelope.body.inform.device_id

        pprint(envelope.model_dump(), sort_dicts=False)

        return JsonResponse({'status': 'ok'}, status=HTTPStatus.OK)
