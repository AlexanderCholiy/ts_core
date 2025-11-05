from typing import Optional, Union

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import DatabaseError
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from core.logger import mongo_logger, subscriber_logger
from users.utils import role_required

from .constants import MAX_SUBSCRIBER_PER_PAGE
from .forms import SubscriberForm
from .models import Subscriber
from .subscribers import SubscriberManager


@login_required
@role_required()
@ratelimit(key='user_or_ip', rate='20/m', block=True)
def index(request: HttpRequest) -> HttpResponse:
    template_name = 'open5gs/index.html'

    query = request.GET.get('q', '').strip()
    try:
        if query:
            subscribers = (
                Subscriber.objects.values('pk', 'imsi')
                .filter(imsi__icontains=query).order_by('-pk')
            )
        else:
            subscribers = (
                Subscriber.objects.values('pk', 'imsi').order_by('-pk')
            )

        paginator = Paginator(subscribers, MAX_SUBSCRIBER_PER_PAGE)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    except DatabaseError as e:
        mongo_logger.exception(e)
        raise

    query_params = request.GET.copy()
    query_params.pop('page', None)
    page_url_base = f'?{query_params.urlencode()}&' if query_params else '?'

    context = {
        'page_obj': page_obj,
        'search_query': query,
        'page_url_base': page_url_base,
    }
    return render(request, template_name, context)


@login_required
@role_required()
@ratelimit(key='user_or_ip', rate='20/m', block=True)
def subscriber(
    request: HttpRequest, imsi: Optional[int] = None
) -> Union[HttpResponse, HttpResponseRedirect]:
    template_name = 'open5gs/subscriber_form.html'
    instance = get_object_or_404(Subscriber, imsi=str(imsi)) if imsi else None

    if request.method == 'POST':
        form = SubscriberForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Абонент ({form.cleaned_data["imsi"]}) сохранен'
            )
            subscriber_logger.info(
                f'Абонент ({form.cleaned_data}) сохранен'
            )
        else:
            messages.error(request, 'Проверьте данные')
    else:
        form = SubscriberForm(instance=instance)

    context = {'form': form}
    return render(request, template_name, context)


@login_required
@role_required()
@ratelimit(key='user_or_ip', rate='20/m', block=True)
def delete_subscriber(
    request: HttpRequest, imsi: int
) -> Union[HttpResponse, HttpResponseRedirect]:
    instance = get_object_or_404(Subscriber, imsi=str(imsi))
    if request.method == 'POST':
        instance.delete()
        subscriber_logger.info(f'Абонент ({imsi}) удален')
        return redirect('open5gs:index')
    context = {'subscriber': instance}
    return render(request, 'open5gs/subscriber_delete.html', context)


@require_POST
@login_required
@role_required()
@ratelimit(key='user_or_ip', rate='20/m', block=True)
def subscribers_upload(request: HttpRequest):
    sub = SubscriberManager()
    return sub.handle_subscribers_excel(
        request=request,
        action_func=sub.upload_subscribers_from_excel,
    )


@require_POST
@login_required
@role_required()
@ratelimit(key='user_or_ip', rate='20/m', block=True)
def subscribers_delete(request: HttpRequest):
    sub = SubscriberManager()
    return sub.handle_subscribers_excel(
        request=request,
        action_func=sub.delete_subscribers_from_excel,
    )


@login_required
@role_required()
@ratelimit(key='user_or_ip', rate='20/m', block=True)
def subscribers_download(request: HttpRequest):
    sub = SubscriberManager()
    return sub.handle_subscribers_download(request)
