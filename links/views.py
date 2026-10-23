from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django_ratelimit.decorators import ratelimit

from links.models import ExternalResource


@login_required
@ratelimit(key='user_or_ip', rate='20/m', block=True)
def resource_iframe_view(request, pk):
    """Отображает страницу со встроенным iframe для выбранного ресурса."""
    resource = get_object_or_404(
        ExternalResource, pk=pk, is_active=True
    )

    return render(
        request, 'links/resource_iframe.html', {'resource': resource}
    )
