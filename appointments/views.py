from urllib import quote
import datetime

from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user
from django.views.generic import DetailView, ListView, DeleteView, UpdateView, CreateView
from django.db.models.query import Q

from .conf import settings

from . import forms
from .periods import weekday_names
from .utils import coerce_date_dict
from . import decorators
from . import models
from . import mixins


class CalendarListView(ListView):
    model = models.Calendar
    template_name = 'appointments/calendar_list.html'


class CalendarView(DetailView):

    """
    This view returns a calendar.  This view should be used if you are
    interested in the meta data of a calendar, not if you want to display a
    calendar.  It is suggested that you use calendar_by_periods if you would
    like to display a calendar.

    Context Variables:

    ``calendar``
        The Calendar object designated by the ``slug`` kwarg.
    """
    template_name = "appointments/calendar.html"
    model = models.Calendar
    context_object_name = 'calendar'


class CalenderPeriodsListView(DetailView):
    model = models.Calendar
    template_name = "appointments/calendar_by_period.html"
    context_object_name = 'calendar'
    periods = None

    """
    This view is for getting a calendar, but also getting periods with that
    calendar.  Which periods you get, is designated with the list periods. You
    can designate which date you the periods to be initialized to by passing
    a date in request.GET. See the template tag ``query_string_for_date``

    Context Variables

    ``date``
        This was the date that was generated from the query string.

    ``periods``
        this is a dictionary that returns the periods from the list you passed
        in.  If you passed in Month and Day, then your dictionary would look
        like this

        {
            'month': <appointments.periods.Month object>
            'day':   <appointments.periods.Day object>
        }

        So in the template to access the Day period in the context you simply
        use ``periods.day``.

    ``calendar``
        This is the Calendar that is designated by the ``calendar_slug``.

    ``weekday_names``
        This is for convenience. It returns the local names of weekedays for
        internationalization.

    """

    def get_context_data(self, **kwargs):
        context = super(
            CalenderPeriodsListView, self).get_context_data(**kwargs)

        date = coerce_date_dict(self.request.GET)
        if date:
            try:
                date = datetime.datetime(**date)
            except ValueError:
                raise Http404
        else:
            date = datetime.datetime.now()

        event_list = settings.APPOINTMENTS_GET_EVENTS_FUNC(
            self.request, self.object)

        period_objects = dict([(period.__name__.lower(), period(event_list, date))
                              for period in self.periods])

        context.update({
            'date': date,
            'periods': period_objects,
            'weekday_names': weekday_names,
            'here': quote(self.request.get_full_path()),
        })
        return context


class OccurrenceDetailView(mixins.LoginRequiredMixin, mixins.OccurrenceViewMixin, DetailView):

    """
    This view is used to display an occurrence.

    Context Variables:

    ``event``
        the event that produces the occurrence

    ``occurrence``
        the occurrence to be displayed

    ``back_url``
        the url from which this request was refered
    """
    model = models.Occurrence
    template_name = "appointments/occurrence.html"


class OccurrenceUpdateView(mixins.LoginRequiredMixin, mixins.OccurrenceViewMixin, UpdateView):
    model = models.Occurrence
    template_name = "appointments/occurrence_edit.html"
    form_class = forms.OccurrenceForm

    def get_context_data(self, **kwargs):
        context = super(OccurrenceUpdateView, self).get_context_data(**kwargs)
        next = next or get_next_url(
            self.request, self.object.get_absolute_url())
        context.update({
            'next': next,
        })

    # def get_form_kwargs(self):
        # form = forms.OccurrenceForm(data=request.POST or None,
        # instance=occurrence)

    # def is_valid(self):
        # occurrence = self.form.save(commit=False)
        # occurrence.event = event
        # occurrence.save()

    def get_success_url(self):
        next = self.kwargs.get('next', None)
        return next or get_next_url(self.request, self.object.get_absolute_url())


class OccurrenceCancelationView(mixins.LoginRequiredMixin, mixins.OccurrenceViewMixin, UpdateView):

    """
    This view is used to cancel an occurrence. If it is called with a POST it
    will cancel the view. If it is called with a GET it will ask for
    conformation to cancel.
    """
    model = models.Occurrence
    template_name = 'appointments/occurrence_cancel.html'

    def get_success_url(self):
        return self.kwargs.get('next', None) or get_next_url(self.request, self.object.event.get_absolute_url())

    def get_context_data(self, **kwargs):
        context = super(
            OccurrenceCancelationView, self).get_context_data(**kwargs)
        context.update({
            'next': self.get_success_url()
        })
        return context

    def form_valid(self, form):
        self.object.cancel()
        return super(OccurrenceCancelationView, self).form_valid(form)


class EventCreateView(mixins.LoginRequiredMixin, CreateView):

    """
    if this view gets a GET request with ``year``, ``month``, ``day``,
    ``hour``, ``minute``, and ``second`` it will auto fill the form, with
    the date specifed in the GET being the start and 30 minutes from that
    being the end.

    If this form receives an event_id it will edit the event with that id, if it
    recieves a calendar_id and it is creating a new event it will add that event
    to the calendar with the id calendar_id

    If it is given a valid form in a POST request it will redirect with one of
    three options, in this order

    # Try to find a 'next' GET variable
    # If the key word argument redirect is set
    # Lastly redirect to the event detail of the recently create event
    """
    model = models.Event
    form_class = forms.EventForm
    calendar_slug_kwarg = 'calendar_slug'
    template_name = 'appointments/event_create.html'

    def get_initial(self):
        if not self.kwargs.get(self.calendar_slug_kwarg, None):
            raise Http404("Creating an event requires a valid Calendar slug")
        initial_data = super(EventCreateView, self).get_initial()
        self.calendar = models.Calendar.objects.get(
            slug__iexact=self.kwargs.get(self.calendar_slug_kwarg))

        date = coerce_date_dict(self.request.GET)
        if date:
            start = datetime.datetime(**date)
            initial_data.update({
                "hour24": True,
                "start": start,
                "end": start + datetime.timedelta(minutes=settings.APPOINTMENTS_EVENT_DURATION)
            })
        return initial_data

    def get_context_data(self, **kwargs):
        context = super(EventCreateView, self).get_context_data(**kwargs)
        context.update({
            "calendar": self.calendar,
        })
        return context

    def form_valid(self, form):
        """
        Super this class and method and repoint the url at your new class
        to do things like:
            associate an activity with an event
            associate a payment with an event
            associate guests who might attend
            associate a location with the event
        """
        user = get_user(self.request)

        # assign the creator
        self.object = form.save(commit=False)
        self.object.creator = user
        self.object.calendar = self.calendar
        self.object.save()

        return super(EventCreateView, self).form_valid(form)

    def get_success_url(self):
        return get_next_url(self.request, self.kwargs.get("next", self.object.get_absolute_url()))


class EventUpdateView(mixins.LoginRequiredMixin, UpdateView):
    model = models.Event
    form_class = forms.EventForm

    def form_valid(self, form):
        return super(EventUpdateView, self).form_valid(form)


class EventDeleteView(mixins.LoginRequiredMixin, DeleteView):

    """
    After the event is deleted there are three options for redirect, tried in
    this order:

    # Try to find a 'next' GET variable
    # If the key word argument redirect is set
    # Lastly redirect to the calendar detail of the recently deleted event
    """
    model = models.Event
    template_name = "appointments/event_delete.html"

    def dispatch(self, request, *args, **kwargs):
        return super(EventDeleteView, self).dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not settings.APPOINTMENTS_CHECK_PERMISSION_FUNC(self.object, self.request.user):
            return HttpResponseRedirect(settings.LOGIN_URL)
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self, *args, **kwargs):
        next = self.request.GET.get("next") or kwargs.get('redirect')
        if not next:
            next = reverse('day_calendar', kwargs={
                           "slug": self.object.calendar.slug})
        return get_next_url(self.request, next)


class EventDetailView(mixins.LoginRequiredMixin, DetailView):

    """
    This view is for showing an event. It is important to remember that an
    event is not an occurrence.  Events define a set of reccurring occurrences.
    If you would like to display an occurrence (a single instance of a
    recurring event) use occurrence.

    Context Variables:

    event
        This is the event designated by the pk url kwarg

    back_url
        this is the url that referred to this view.
    """
    model = models.Event
    context_object_name = 'event'
    template_name = "appointments/event.html"

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        context.update({
            "back_url": self.request.META.get('HTTP_REFERER', None),
        })
        return context


def check_next_url(next):
    """
    Checks to make sure the next url is not redirecting to another page.
    Basically it is a minimal security check.
    """
    if not next or '://' in next:
        return None
    return next


def get_next_url(request, default):
    next = default
    if settings.APPOINTMENTS_OCCURRENCE_CANCEL_REDIRECT:
        next = settings.APPOINTMENTS_OCCURRENCE_CANCEL_REDIRECT
    if 'next' in request.REQUEST and check_next_url(request.REQUEST['next']) is not None:
        next = request.REQUEST['next']
    return next
