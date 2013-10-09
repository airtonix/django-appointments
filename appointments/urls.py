from django.conf.urls.defaults import url, patterns

# from .feeds import UpcomingEventsFeed
# from .feeds import CalendarICalendar
from appointments.periods import Year, Month, Week, Day
from appointments import views

urlpatterns = patterns('',

                       # urls for Calendars
                       url(r'^/$',
                           views.CalendarListView.as_view(),
                           name="schedule"),

                       url(r'^calendar/(?P<slug>[-\w]+)/$',
                           views.CalendarView.as_view(),
                           name="calendar_home",
                           ),

                       # We specify the template_name here instead of inside the view
                       # because this view suits our ideals of how to manipulate the data,
                       # but not on how to present it.
                       url(r'^calendar/(?P<slug>[-\w]+)/year/$',
                           views.CalenderPeriodsListView.as_view(
                               template_name='appointments/calendar_year.html',
                               periods=[Year]),
                           name="year_calendar"),

                       url(r'^calendar/(?P<slug>[-\w]+)/tri_month/$',
                           views.CalenderPeriodsListView.as_view(
                               template_name='appointments/calendar_tri_month.html',
                               periods=[Month]),
                           name="tri_month_calendar"),

                       url(r'^calendar/(?P<slug>[-\w]+)/compact_month/$',
                           views.CalenderPeriodsListView.as_view(
                               template_name='appointments/calendar_compact_month.html',
                               periods=[Month]),
                           name="compact_calendar"),

                       url(r'^calendar/(?P<slug>[-\w]+)/month/$',
                           views.CalenderPeriodsListView.as_view(
                               template_name='appointments/calendar_month.html',
                               periods=[Month]),
                           name="month_calendar"),

                       url(r'^calendar/(?P<slug>[-\w]+)/week/$',
                           views.CalenderPeriodsListView.as_view(
                               template_name='appointments/calendar_week.html',
                               periods=[Week]),
                           name="week_calendar"),

                       url(r'^calendar/(?P<slug>[-\w]+)/daily/$',
                           views.CalenderPeriodsListView.as_view(
                               template_name='appointments/calendar_day.html',
                               periods=[Day]),
                           name="day_calendar"),

                       # Event Urls
                       url(r'^calendar/(?P<calendar_slug>[-\w]+)/event/create/$',
                           views.EventCreateView.as_view(),
                           name='calendar_create_event'),
                       url(r'^calendar/(?P<calendar_slug>[-\w]+)/event/(?P<pk>\d+)/edit/$',
                           views.EventUpdateView.as_view(),
                           name='edit_event'),
                       url(r'^calendar/(?P<calendar_slug>[-\w]+)/event/(?P<pk>\d+)/delete/$',
                           views.EventDeleteView.as_view(),
                           name="delete_event"),
                       url(r'^calendar/(?P<calendar_slug>[-\w]+)/event/(?P<pk>\d+)/$',
                           views.EventDetailView.as_view(),
                           name="event"),

                       # urls for already persisted occurrences
                       url(r'^occurrence/(?P<pk>\d+)/(?P<occurrence_id>\d+)/$',
                           views.OccurrenceDetailView.as_view(),
                           name="occurrence"),
                       url(r'^occurrence/cancel/(?P<pk>\d+)/(?P<occurrence_id>\d+)/$',
                           views.OccurrenceCancelationView.as_view(),
                           name="cancel_occurrence"),
                       url(r'^occurrence/edit/(?P<pk>\d+)/(?P<occurrence_id>\d+)/$',
                           views.OccurrenceUpdateView.as_view(),
                           name="edit_occurrence"),

                       # urls for unpersisted occurrences
                       url(r'^occurrence/(?P<pk>\d+)/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)/(?P<minute>\d+)/(?P<second>\d+)/$',
                           views.OccurrenceDetailView.as_view(),
                           name="occurrence_by_date"),
                       url(r'^occurrence/cancel/(?P<pk>\d+)/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)/(?P<minute>\d+)/(?P<second>\d+)/$',
                           views.OccurrenceCancelationView.as_view(),
                           name="cancel_occurrence_by_date"),
                       url(r'^occurrence/edit/(?P<pk>\d+)/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)/(?P<minute>\d+)/(?P<second>\d+)/$',
                           views.OccurrenceUpdateView.as_view(),
                           name="edit_occurrence_by_date"),


                       # feed urls
                       # url(r'^feed/calendar/(.*)/$',
                       #     'django.contrib.syndication.views.feed',
                       #     {"feed_dict": {"upcoming": UpcomingEventsFeed}}),

                       # url(r'^ical/calendar/(.*)/$', CalendarICalendar()),

                       )
