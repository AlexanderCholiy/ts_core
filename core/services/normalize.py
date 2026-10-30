from typing import Any


def normalize_required_string(value: Any) -> Any:
    if value is None:
        raise ValueError('Поле не может быть пустым.')

    if not isinstance(value, str):
        return value

    value = value.strip()

    if not value:
        raise ValueError('Поле не может быть пустым.')

    return value


def normalize_optional_string(value: Any) -> Any:
    if value is None:
        return None

    if not isinstance(value, str):
        return value

    value = value.strip()

    return value or None
