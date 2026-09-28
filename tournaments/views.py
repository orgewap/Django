from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from typing import Any
from tournaments.models import Tournament
from django.views.generic import TemplateView


# Create your views here.
class ShowTournamentsView(TemplateView):
    template_name = "tournaments/show_tournaments.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['tournaments'] = Tournament.objects.all()

        return context
        