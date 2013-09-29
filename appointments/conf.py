from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from appconf import AppConf


class AppointmentAppConf(AppConf):

    FIRST_DAY_OF_WEEK = 0

    def configure_first_day_of_week(self, value):
        if not settings.APPOINTMENT_FIRST_DAY_OF_WEEK:
            raise ImproperlyConfigured(_("APPOINTMENT_FIRST_DAY_OF_WEEK must be an integer between 0 and 6"))

    # default duration (in minutes) for new events
    EVENT_DURATION = 30

    # whether to display cancelled occurrences
    # (if they are displayed then they have a css class "cancelled")
    # this controls behaviour of Period.classify_occurrence method
    SHOW_CANCELLED_OCCURRENCES = False

    # Callable used to check if a user has edit permissions to event
    # (and occurrence). Used by check_edit_permission decorator
    # if ob==None we check permission to add occurrence
    CHECK_PERMISSION_FUNC = lambda instance, user: user.is_authenticated()

    # Callable used to customize the event list given for a calendar and user
    # (e.g. all events on that calendar, those events plus another calendar's events,
    # or the events filtered based on user permissions)
    # Imports have to be placed within the function body to avoid circular imports
    GET_EVENTS_FUNC = lambda request, calendar: calendar.event_set.all()

    # URL to redirect to to after an occurrence is canceled
    OCCURRENCE_CANCEL_REDIRECT = None
