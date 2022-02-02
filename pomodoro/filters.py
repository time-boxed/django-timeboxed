from datetime import datetime, timezone

from dateutil.parser import parse
from rest_framework.filters import BaseFilterBackend


class DateFilter(BaseFilterBackend):
    lookup_prefixes = {
        "start": "start__gte",
        "end": "end__lte",
    }

    def parse_time(self, value):
        if value.isdigit():
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        else:
            return parse(value)

    def filter_queryset(self, request, queryset, view):
        for key in self.lookup_prefixes:
            if key in request.GET:
                value = self.parse_time(request.GET[key])
                queryset = queryset.filter(**{self.lookup_prefixes[key]: value})
        return queryset
