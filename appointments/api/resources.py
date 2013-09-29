import logging
from datetime import datetime

from surlex.dj import surl

from django.db.models.query import Q
from django.contrib.auth.models import User, Group

from tastypie import fields
from tastypie.resources import ModelResource, ALL
from tastypie.utils import trailing_slash

from ..models import Calendar, Event, EventRelation, Occurrence
from .mixins import ContainsNestedResourcesMixin


# l = logging.getLogger('django.db.backends')
# l.setLevel(logging.DEBUG)
# l.addHandler(logging.StreamHandler())


class CalendarResource(ContainsNestedResourcesMixin, ModelResource):
#     events = fields.ToManyField(to='appointments.api.resources.EventResource', attribute='event_set', full=True)

    class Meta:
        queryset = Calendar.objects.all()
        resource_name = 'calendar'
#         # urlargs = {"name": resource_name, "slash": trailing_slash()}

#     def obj_get_list(self, bundle, **kwargs):
#         user = User.objects.get(pk=bundle.request.user.pk)
#         # queryset = super(CalendarResource, self).obj_get_list(bundle, **kwargs)
#         return Calendar.objects.get_or_create_calendar_for_object(user)

    # def prepend_urls(self):
    #     return [
    #         surl(r"^<resource_name={name}>/<pk:#>/date/<date:s>{slash}$".format(**self._meta.urlargs), self.wrap_view('dispatch_event_list'), name='api_event_list'),
    #     ]

    # def dispatch_event_list(self, request, **kwargs):
    #     return self.dispatch('event_list', request, **kwargs)

    # def get_file_list(self, request, **kwargs):
    #     date = kwargs.pop('date')
    #     events_covering_date = Q()
    #     file_resource = FileResource()
    #     return self.get_child_list(request, resource=file_resource, queryset_filter=file_filter, **kwargs)


class OccurrenceResource(ModelResource):

    class Meta:
        queryset = Occurrence.objects.all()
        resource_name = 'occurrence'


class EventResource(ContainsNestedResourcesMixin, ModelResource):
    calendar = fields.ForeignKey(CalendarResource, "calendar")
    attendees = fields.ToManyField(to="appointments.api.resources.EventRelationResource", attribute="eventrelation_set")
    occurences = fields.ToManyField(to="appointments.api.resources.OccurrenceResource", attribute="occurrence_set")
    creator = fields.ToManyField(to="appointments.api.resources.OccurrenceResource", attribute="occurrence_set")
    organiser = fields.ToManyField(to="appointments.api.resources.OccurrenceResource", attribute="occurrence_set")

    class Meta:
        queryset = Event.objects.all()
        resource_name = 'event'
        filtering = {
            'title': ALL,
            'creator': ALL,
            'calendar': ALL,
            'created_on': ALL,
            'start': ALL,
            'end': ALL,
        }

    def get_relation(self, bundle, distinction=None):
        if not distinction:
            return None

        try:
            return list(bundle.obj.eventrelation_set.filter(distinction=distinction))

        except EventRelation.DoesNotExist:
            return None

    def dehydrate_attendees(self, bundle):
        return self.get_relation(bundle, 'attendees')

    def dehydrate_creator(self, bundle):
        return self.get_relation(bundle, 'creator')

    def dehydrate_organiser(self, bundle):
        return self.get_relation(bundle, 'organiser')

    def get_object_list(self, request):
        date = request.GET.get("date", None)
        queryset = super(EventResource, self).get_object_list(request)
        if date:
            queryset = queryset.extra(
                where=["date(start) <= %s AND date(end) >= %s", ],
                params=[date, date]
            )
        return queryset


EnabledResources = (
    EventResource,
)
