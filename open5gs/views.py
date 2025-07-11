from typing import Optional

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required

from users.utils import role_required
from .forms import SubscriberForm
from .models import Subscriber


@login_required
@role_required()
def index(request: HttpRequest) -> HttpResponse:
    template_name = 'open5gs/index.html'
    subscribers = Subscriber.objects.values('pk', 'imsi').order_by('-pk')
    context = {'subscribers': subscribers}
    return render(request, template_name, context)


@login_required
@role_required()
def subscriber(
    request: HttpRequest, imsi: Optional[str] = None
) -> HttpResponse:
    template_name = 'open5gs/subscriber_form.html'

    if imsi is not None:
        instance = get_object_or_404(Subscriber, imsi=imsi)
    else:
        instance = None

    form = SubscriberForm(request.POST or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()

    return render(request, template_name, context)


@login_required
@role_required()
def delete_subscriber(request: HttpRequest, imsi: str):
    instance = get_object_or_404(Subscriber, imsi=imsi)
    form = SubscriberForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        instance.delete()
        return redirect('open5gs:index')
    return render(request, 'open5gs/subscriber_form.html', context)
