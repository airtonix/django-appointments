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

                       # We specify the template_name here instead of inside the view
                       # because this view suits our ideals of how to manipulate the data,
                       # but not on how to present it.
                       url(r'^calendar/year/(?P<slug>[-\w]+)/$',
                           views.CalenderPeriodsListView.as_view(
                               template_name='appointments/calendar_year.html',
                               periods=[Year]),
                           name="year_calendar"),

                       url(r'^calendar/tri_month/(?P<slug>[-\w]+)/$',
                           views.CalenderPeriodsListView.as_view(
                               template_name='appointments/calendar_tri_month.html',
                               periods=[Month]),
                           name="tri_month_calendar"),

                       url(r'^calendar/compact_month/(?P<slug>[-\w]+)/$',
                           views.CalenderPeriodsListView.as_view(
                               template_name='appointments/calendar_compact_month.html',
                               periods=[Month]),
                           name="compact_calendar"),

                       url(r'^calendar/month/(?P<slug>[-\w]+)/$',
                           views.CalenderPeriodsListView.as_view(
                               template_name='appointments/calendar_month.html',
                               periods=[Month]),
                           name="month_calendar"),

                       url(r'^calendar/week/(?P<slug>[-\w]+)/$',
                           views.CalenderPeriodsListView.as_view(
                               template_name='appointments/calendar_week.html',
                               periods=[Week]),
                           name="week_calendar"),

                       url(r'^calendar/daily/(?P<slug>[-\w]+)/$',
                           views.CalenderPeriodsListView.as_view(
                               template_name='appointments/calendar_day.html',
                               periods=[Day]),
                           name="day_calendar"),

                       url(r'^calendar/(?P<slug>[-\w]+)/$',
                           views.CalendarView.as_view(),
                           name="calendar_home",
                           ),

                       # Event Urls
                       url(r'^event/create/(?P<calendar_slug>[-\w]+)/$',
                           views.EventCreateView.as_view(),
                           name='calendar_create_event'),
                       url(r'^event/edit/(?P<calendar_slug>[-\w]+)/(?P<pk>\d+)/$',
                           views.EventUpdateView.as_view(),
                           name='edit_event'),
                       url(r'^event/delete/(?P<calendar_slug>[-\w]+)/(?P<pk>\d+)/$',
                           views.EventDeleteView.as_view(),
                           name="delete_event"),
                       url(r'^event/(?P<calendar_slug>[-\w]+)/(?P<pk>\d+)/$',
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
