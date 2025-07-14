from typing import Optional, Union
from urllib.parse import urlencode

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from users.utils import role_required
from .forms import SubscriberForm
from .models import Subscriber
from .constants import MAX_SUBSCRIBER_PER_PAGE


@login_required
@role_required()
def index(request: HttpRequest) -> HttpResponse:
    template_name = 'open5gs/index.html'

    query = request.GET.get('q', '').strip()
    if query:
        subscribers = [i for i in range(100)]
        # subscribers = (
        #     Subscriber.objects.values('pk', 'imsi')
        #     .filter(imsi__icontains=query).order_by('-pk')
        # )
    else:
        subscribers = [i for i in range(100)]
        # subscribers = Subscriber.objects.values('pk', 'imsi').order_by('-pk')

    paginator = Paginator(subscribers, MAX_SUBSCRIBER_PER_PAGE)
    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    page_url_base = '?'
    if query_params:
        page_url_base += urlencode(query_params) + '&'

    context = {'page_obj': page_obj, 'search_query': query, 'page_url_base': page_url_base}
    return render(request, template_name, context)


@login_required
@role_required()
def subscriber(
    request: HttpRequest, imsi: Optional[int] = None
) -> Union[HttpResponse, HttpResponseRedirect]:
    template_name = 'open5gs/subscriber_form.html'
    instance = get_object_or_404(Subscriber, imsi=str(imsi)) if imsi else None

    if request.method == 'POST':
        form = SubscriberForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('open5gs:index')
    else:
        form = SubscriberForm(instance=instance)

    context = {'form': form}
    return render(request, template_name, context)


@login_required
@role_required()
def delete_subscriber(
    request: HttpRequest, imsi: int
) -> Union[HttpResponse, HttpResponseRedirect]:
    instance = get_object_or_404(Subscriber, imsi=str(imsi))
    if request.method == 'POST':
        instance.delete()
        return redirect('open5gs:index')
    context = {'subscriber': instance}
    return render(request, 'open5gs/subscriber_delete.html', context)
