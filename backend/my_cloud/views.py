from django.views.generic import TemplateView


class SPAView(TemplateView):
    """
    Отдаёт index.html для всех SPA-маршрутов.
    """
    template_name = 'index.html'