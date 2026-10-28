import json
from http import HTTPStatus

from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from core.logger import base_station_logger


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(require_POST, name='dispatch')
@method_decorator(
    ratelimit(key='ip', rate='120/m', block=True), name='dispatch'
)
class BaseStationMetricsView(View):
    """Эндпоинт приёма метрик базовой станции."""

    def post(self, request: HttpRequest, *args, **kwargs):
        base_station_logger.info(
            'Incoming metrics | ip=%s path=%s content_type=%s body=%s',
            request.META.get("REMOTE_ADDR"),
            request.path,
            request.content_type,
            self._body_preview(request),
        )
        # TODO: дальше парсинг и сохранение метрик
        return JsonResponse({'status': 'ok'}, status=HTTPStatus.OK)

    @staticmethod
    def _body_preview(request: HttpRequest, max_size: int = 1000) -> str:
        """Тело запроса для лога: JSON сжимаем, бинарь не логируем целиком."""
        try:
            body = request.body
        except Exception as exc:
            return f'<unreadable body: {exc}>'

        if not body:
            return '<empty>'

        try:
            text = body.decode()
        except UnicodeDecodeError:
            return f'<binary body, {len(body)} bytes>'

        try:
            text = json.dumps(
                json.loads(text), ensure_ascii=False, separators=(',', ':')
            )
        except (json.JSONDecodeError, ValueError):
            pass

        if len(text) > max_size:
            return (
                text[:max_size] + f'... <truncated, total {len(text)} chars>'
            )
        return text
