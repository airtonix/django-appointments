import datetime

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext as _

from .utils import handle_redirect_to_login
from .conf import settings
from . import models


class LoginRequiredMixin(object):
    redirect_field_name = "next"
    login_url = None

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs

        if request.user.is_authenticated():
            return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

        return self.redirect_to_login()

    def get_login_url(self):
        return self.login_url or settings.LOGIN_URL

    def get_next_url(self):
        return self.request.get_full_path()

    def redirect_to_login(self):
        return handle_redirect_to_login(
            self.request,
            redirect_field_name=self.redirect_field_name,
            login_url=self.get_login_url(),
            next_url=self.get_next_url(),
        )


class OccurrenceViewMixin(object):
    model = models.Occurrence
    pk_kwarg = 'occurrence_id'
    context_object_name = 'occurrence'

    def get_object(self, queryset):
        """
        Because occurrences don't have to be persisted, there must be two ways to
        retrieve them. both need an event, but if its persisted the occurrence can
        be retrieved with an id. If it is not persisted it takes a date to
        retrieve it.  This function returns an event and occurrence regardless of
        which method is used.
        """
        try:
            return super(OccurrenceViewMixin, self).get_object(queryset)

        except self.model.DoesNotExist:

            year = self.kwargs.get("year")
            month = self.kwargs.get("month")
            day = self.kwargs.get("day")
            hour = self.kwargs.get("hour")
            minute = self.kwargs.get("minute")
            second = self.kwargs.get("second")
            event_id = self.kwargs.get("event_id")

            if(all((year, month, day, hour, minute, second))):
                self.event = models.Event.objects.get(id=event_id)
                return self.event.get_occurrence(
                    datetime.datetime(
                        int(year), int(month), int(day), int(hour),
                        int(minute), int(second)))
        # except self.model.DoesNotExist:
            # raise Http404(_("No %(verbose_name)s found matching the query") %
                          # {'verbose_name': queryset.model._meta.verbose_name})
