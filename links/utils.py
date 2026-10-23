from django.http import HttpRequest

from links.models import ExternalResource


def external_resources_processor(
    request: HttpRequest
) -> dict[str, ExternalResource]:
    """
    Добавляет внешние ссылки в глобальный контекст шаблонов,
    если текущий пользователь является активным сотрудником (staff)
    или суперпользователем.
    """
    user = request.user

    if (
        user.is_authenticated
        and user.is_active
        and (user.is_staff or user.is_superuser)
    ):
        resources = ExternalResource.objects.filter(is_active=True)
    else:
        resources = ExternalResource.objects.none()

    return {
        'SIDEBAR_EXTERNAL_RESOURCES': resources
    }
