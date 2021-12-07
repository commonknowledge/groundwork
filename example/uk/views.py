from django.views.generic import ListView

from example.uk.models import Constituency


class MpListView(ListView):
    model = Constituency
    template_name = "uk_constituencies/mp_list.html"
