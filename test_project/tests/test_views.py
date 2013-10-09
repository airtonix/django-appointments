import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.db.models import get_model

from model_mommy import mommy
from appointments.views import check_next_url, coerce_date_dict

from . import mixins


class TestViewUtils(TestCase):

    def test_check_next_url(self):
        url = "http://example.com"
        self.assertTrue(check_next_url(url) is None)
        url = "/hello/world/"
        self.assertEqual(url, check_next_url(url))

    def test_coerce_date_dict(self):
        self.assertEqual(
            coerce_date_dict(
                {'year': '2008', 'month': '4', 'day': '2', 'hour': '4', 'minute': '4', 'second': '4'}),
            {'year': 2008, 'month': 4, 'day': 2,
                'hour': 4, 'minute': 4, 'second': 4}
        )

    def test_coerce_date_dict_partial(self):
        self.assertEqual(
            coerce_date_dict({'year': '2008', 'month': '4', 'day': '2'}),
            {'year': 2008, 'month': 4, 'day': 2,
                'hour': 0, 'minute': 0, 'second': 0}
        )

    def test_coerce_date_dict_empty(self):
        self.assertEqual(
            coerce_date_dict({}),
            {}
        )

    def test_coerce_date_dict_missing_values(self):
        self.assertEqual(
            coerce_date_dict({'year': '2008', 'month': '4', 'hours': '3'}),
            {'year': 2008, 'month': 4, 'day': 1,
                'hour': 0, 'minute': 0, 'second': 0}
        )


class BaseAppointmentTests(object):

    def setUp(self):
        # Sass Users
        self.user_owner = self.make_user(
            'owner', 'owner', is_superuser=False, is_active=True, is_staff=False)
        self.user_invitee = self.make_user(
            'invitee', 'invitee', is_superuser=False, is_active=True, is_staff=False)

        # Sass Manager
        self.user_admin = self.make_user(
            'admin', 'admin', is_superuser=True, is_active=True, is_staff=True)

        self.public_calendar_name = "A Public Calendar"
        self.public_calender_slug = "public-calendar"
        self.public_calendar = mommy.make("appointments.Calendar",
                                          name=self.public_calendar_name,
                                          slug=self.public_calender_slug)


Event = get_model('appointments', 'Event')
Calendar = get_model('appointments', 'Calendar')


class TestCalendarPrivacy(BaseAppointmentTests, mixins.TestCaseWithUsersMixin, mixins.LazyTestCase):
    """
        This test bundle deals with calendars that are marked private.

        A calendar owner should be able to

            * view their own calendar and any events on it.
            * modify any events on their calendars
            * invite other users to events on their calendar
            * Create a mask that defines when appointments can be made for
              certain requirements. for example
                * free/busy times, defined as mon-fri, 9am-5pm
                * drop in meetings, defined as tues, weds 10am-lunch

        Other authenticated users should be able to

            * view other users calendars
            * view entries they created on other peoples calendars
            * view entries not marked private on other peoples calendars

    """

    def setUp(self):
        super(TestCalendarPrivacy, self).setUp()
        self.private_calendar_name = "A Private Calendar"
        self.private_calendar_slug = "private-calendar"
        self.private_calendar = mommy.make("appointments.Calendar",
                                           name=self.private_calendar_name,
                                           slug=self.private_calendar_slug)

        self.private_calendar.create_relation(self.user_owner, distinction='owner')

    def test_calendar_view(self):
        """
            test all presentations of calendar after:
             * masks have been applied (don't show unavailable time slots)
             * don't show details of private events.
        """
        def get_calendar_view():
            return self.client.get(reverse('calendar_home', kwargs={"slug": self.private_calendar_slug}))

        response = get_calendar_view()
        self.assertEqual(response.status_code, 200)
        with self.login(self.user_owner.username, self.user_owner._unecrypted_password):
            response = get_calendar_view()
            self.assertEqual(response.status_code, 200)

    def test_create_own_event(self):
        """
            create a private event.
            no one else should be able to access it
        """
        self.assertTrue(self.private_calendar.has_relation(self.user_owner, distinction='owner'))
        with self.login(self.user_owner.username, self.user_owner._unecrypted_password):
            url = reverse("calendar_create_event",
                          kwargs={"calendar_slug": self.private_calendar_slug})
            post_data = {'description': 'description', 'title': 'title',
                         'end_recurring_period_0': '2008-10-30', 'end_recurring_period_1': '10:22:00', 'end_recurring_period_2': 'AM',
                         'end_0': '2008-10-30', 'end_1': '10:22:00', 'end_2': 'AM',
                         'start_0': '2008-10-30', 'start_1': '09:21:57', 'start_2': 'AM',
                         }
            response = self.client.post(url, post_data, follow=True)
            event = Event.objects.get(pk=1)
            # event = response.context['event']
            self.assertTrue(event.has_relation(self.user_owner, distinction='owner'))

    def test_invite_user(self):
        """
            Invite a user to an event regardless of masks.
            optionally notify the user of the invitation.
        """

    def test_user_create_appointment(self):
        """
            let a user create an event in available timeslots, after :
              * masks have been applied and,
              * when available timeslots are found
              * event requirement rules have been fulfilled (callbacks)
        """
        pass


class TestScheduleMasks(BaseAppointmentTests, mixins.TestCaseWithUsersMixin, mixins.LazyTestCase):
    """
        TODO: functional tests on building and applying masks.
    """
    def test_simple_workweek_mask(self):
        pass

    def test_ireggular_workweek_mask(self):
        pass

    def test_oneoff_weekend_mask(self):
        pass

    def test_repeating_fortnight_mask(self):
        pass

    def test_holiday_mask(self):
        pass


class TestUrls(BaseAppointmentTests, mixins.TestCaseWithUsersMixin, mixins.LazyTestCase):

    def test_calendar_view(self):
        url = reverse("year_calendar", kwargs={
                      "slug": self.public_calender_slug})
        response = self.client.get(url, {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context[0]["calendar"].name, self.public_calendar_name)

    def test_calendar_month_view(self):
        url = reverse("month_calendar", kwargs={
                      "slug": self.public_calender_slug})
        response = self.client.get(url, {'year': 2000, 'month': 11})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context[0]["calendar"].name, self.public_calendar_name)
        month = response.context[0]["periods"]['month']
        self.assertEqual((month.start, month.end),
                         (datetime.datetime(2000, 11, 1, 0, 0), datetime.datetime(2000, 12, 1, 0, 0)))

    def test_event_creation_anonymous_user(self):
        url = reverse("calendar_create_event",
                      kwargs={"calendar_slug": self.public_calender_slug})
        response = self.client.get(url, {})
        self.assertEqual(response.status_code, 302)

    def test_event_creation_admin_user(self):

        with self.login(self.user_admin.username, self.user_admin._unecrypted_password):

            url = reverse("calendar_create_event",
                          kwargs={"calendar_slug": self.public_calender_slug})
            response = self.client.get(url, {})
            self.assertEqual(response.status_code, 200)

            url = reverse("calendar_create_event",
                          kwargs={"calendar_slug": self.public_calender_slug})
            post_data = {'description': 'description', 'title': 'title',
                         'end_recurring_period_0': '2008-10-30', 'end_recurring_period_1': '10:22:00', 'end_recurring_period_2': 'AM',
                         'end_0': '2008-10-30', 'end_1': '10:22:00', 'end_2': 'AM',
                         'start_0': '2008-10-30', 'start_1': '09:21:57', 'start_2': 'AM'
                         }
            response = self.client.post(url, post_data)
            self.assertEqual(response.status_code, 302)

            url = reverse(
                "event", kwargs={"pk": 1, "calendar_slug": self.public_calender_slug})
            response = self.client.get(url, {})
            self.assertEqual(response.status_code, 200)

    def test_view_private_event(self):
        # attempting to view a private event should redirect anonymous users to
        # login
        response = self.client.get(
            reverse("event", kwargs={"pk": 1, "calendar_slug": self.public_calender_slug}), {})
        self.assertEqual(response.status_code, 302)

    def test_delete_event_anonymous_user(self):
        # Only logged-in users should be able to delete, so we're redirected
        response = self.client.get(
            reverse("delete_event", kwargs={"calendar_slug": self.public_calender_slug, "pk": 1}), {})
        self.assertEqual(response.status_code, 302)

    def test_delete_event_admin_user(self):
        with self.login(self.user_admin.username, self.user_admin._unecrypted_password):
            event_dict = {'description': 'description',
                          'title': 'title',
                          'end_recurring_period': datetime.datetime(2008, 10, 30, 10, 22),
                          'end': datetime.datetime(2008, 10, 30, 10, 22),
                          'start': datetime.datetime(2008, 10, 30, 9, 21),
                          'calendar': self.public_calendar
                          }
            event = mommy.make('appointments.Event', **event_dict)
            # Load the deletion page

            response = self.client.get(
                reverse("delete_event", kwargs={"calendar_slug": self.public_calender_slug, "pk": event.id}), {})
            self.assertEqual(response.status_code, 200)

            # Delete the event
            response = self.client.post(
                reverse("delete_event", kwargs={"calendar_slug": self.public_calender_slug, "pk": event.id}), {})
            self.assertEqual(response.status_code, 302)

            # Since the event is now deleted, we get a 404
            response = self.client.get(
                reverse("delete_event", kwargs={"calendar_slug": self.public_calender_slug, "pk": event.id}), {})
            self.assertEqual(response.status_code, 404)
