from http import HTTPStatus
from typing import Optional

from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls.exceptions import Resolver404


def bad_request(
    request: HttpRequest, exception: Optional[Exception] = None
) -> HttpResponse:
    return render(request, 'core/400.html', status=HTTPStatus.BAD_REQUEST)


def page_not_found(
    request: HttpRequest, exception: Resolver404 = None
) -> HttpResponse:
    current_site = get_current_site(request)
    path = f'{current_site}{request.path}'
    return render(
        request, 'core/404.html', {'path': path}, status=HTTPStatus.NOT_FOUND)


def permission_denied(
    request: HttpRequest, exception: Optional[Exception] = None
) -> HttpResponse:
    return render(request, 'core/403.html', status=HTTPStatus.FORBIDDEN)


def csrf_failure(request: HttpRequest, reason: str = '') -> HttpResponse:
    return render(
        request,
        'core/403csrf.html',
        {'reason': reason},
        status=HTTPStatus.FORBIDDEN
    )


def server_error(request: HttpRequest) -> HttpResponse:
    return render(
        request, 'core/500.html', status=HTTPStatus.INTERNAL_SERVER_ERROR
    )


def too_many_requests(
    request: HttpRequest, exception: Optional[Exception] = None
) -> HttpResponse:
    return render(
        request, 'core/429.html', status=HTTPStatus.TOO_MANY_REQUESTS
    )
