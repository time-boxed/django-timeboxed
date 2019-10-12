import icalendar
from rest_framework import renderers

from django.conf import settings


class CalendarRenderer(renderers.BaseRenderer):
    media_type = "text/plain" if settings.DEBUG else "text/calendar"
    format = "ics"

    def render(self, data, media_type=None, renderer_context=None):
        # Pull these from our renderer context to better match a
        # typical view
        if renderer_context["response"].status_code != 200:
            return data

        view = renderer_context["view"]
        request = renderer_context["request"]
        page = view.paginate_queryset(view.queryset)

        cal = icalendar.Calendar()
        cal.add("prodid", "-//Pomodoro Calendar//")
        cal.add("version", "2.0")
        cal.add("X-ORIGINAL-URL", request.build_absolute_uri())

        for pomodoro in page:
            event = icalendar.Event()
            event.add("summary", pomodoro.title)
            event.add("description", pomodoro.memo)
            event.add("dtstart", pomodoro.start)
            event.add("dtend", pomodoro.end)
            event.add("url", pomodoro.url)
            event.add("categories", [pomodoro.category])
            event["uid"] = pomodoro.pk
            cal.add_component(event)

        return cal.to_ical()
