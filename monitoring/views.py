from django.http import HttpResponse

from .models import Status


def index(request):
    statuses = Status.objects.all()
    print(list(statuses))
    return HttpResponse('Главная страница')
