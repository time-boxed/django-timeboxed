from dateutil.parser import parse as dateparser

from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.views import redirect_to_login


class OwnerRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            if self.get_object().owner == self.request.user:
                return super().dispatch(request, *args, **kwargs)

        return redirect_to_login(
            self.request.get_full_path(),
            self.get_login_url(),
            self.get_redirect_field_name(),
        )


class DateFilterMixin:
    def get_date_qs(self, qs):
        if "start" in self.request.GET:
            qs = qs.filter(start__gt=dateparser(self.request.GET["start"]))
        if "end" in self.request.GET:
            qs = qs.filter(end__lt=dateparser(self.request.GET["end"]))
        return qs
