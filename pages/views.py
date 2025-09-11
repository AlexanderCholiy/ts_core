from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django_ratelimit.decorators import ratelimit


@method_decorator(
    ratelimit(key='user_or_ip', rate='20/m', block=True), name='dispatch'
)
class AboutTemplateView(TemplateView):
    template_name = 'pages/about.html'

    def get_context_data(self: 'AboutTemplateView', **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        return context
