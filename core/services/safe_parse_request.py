import json

from django.http.request import HttpRequest


def safe_parse_request_body(request: HttpRequest, max_size: int = 1000) -> str:
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
