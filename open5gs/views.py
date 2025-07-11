from typing import Optional, Union

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
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
) -> Union[HttpResponse, HttpResponseRedirect]:
    template_name = 'open5gs/subscriber_form.html'
    instance = get_object_or_404(Subscriber, imsi=imsi) if imsi else None

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
    request: HttpRequest, imsi: str
) -> Union[HttpResponse, HttpResponseRedirect]:
    instance = get_object_or_404(Subscriber, imsi=imsi)
    if request.method == 'POST':
        instance.delete()
        return redirect('open5gs:index')
    context = {'subscriber': instance}
    return render(request, 'open5gs/subscriber_delete.html', context)
