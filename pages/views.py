from django.views.generic import TemplateView


class AboutTemplateView(TemplateView):
    # template_name = 'pages/about.html'
    template_name = 'core/404.html'

    def get_context_data(self: 'AboutTemplateView', **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        return context
