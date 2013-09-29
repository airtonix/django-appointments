from djangogcal.adapter import CalendarAdapter, CalendarEventData
from djangogcal.observer import CalendarObserver

from .event import Event

class EventCalendarAdapter(CalendarAdapter):
    """
    A calendar adapter for the Event model.
    """

    def get_event_data(self, instance):
        """
        Returns a CalendarEventData object filled with data from the adaptee.
        """
        return CalendarEventData(
                start=instance.start,
                end=instance.end,
                title=instance.title
            )

# problem: this is site wide, we need per user but that would be
# overkill on the server, we really need an event driven method

observer = CalendarObserver(email=settings.CALENDAR_EMAIL,
                            password=settings.CALENDAR_PASSWORD)
observer.observe(Event, EventCalendarAdapter())