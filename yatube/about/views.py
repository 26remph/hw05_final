from django.views.generic.base import TemplateView


class AboutAuthor(TemplateView):
    template_name = 'about/about.html'


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'
