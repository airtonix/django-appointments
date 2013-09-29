import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse

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


class TestUrls(mixins.TestCaseWithUsersMixin, mixins.LazyTestCase):

    def setUp(self):
        # Sass Users
        self.user_owner = self.make_user(
            'owner', 'owner', is_superuser=False, is_active=True, is_staff=False)
        self.user_invitee = self.make_user(
            'invitee', 'invitee', is_superuser=False, is_active=True, is_staff=False)

        # Sass Manager
        self.user_admin = self.make_user(
            'admin', 'admin', is_superuser=True, is_active=True, is_staff=True)

        self.calender_name = "Example Calendar"
        self.calender_slug = "example"
        self.calendar = mommy.make("appointments.Calendar",
                                   name=self.calender_name,
                                   slug=self.calender_slug)

    def test_calendar_view(self):
        url = reverse("year_calendar", kwargs={"slug": self.calender_slug})
        response = self.client.get(url, {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context[0]["calendar"].name, self.calender_name)

    def test_calendar_month_view(self):
        url = reverse("month_calendar", kwargs={"slug": self.calender_slug})
        response = self.client.get(url, {'year': 2000, 'month': 11})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context[0]["calendar"].name, self.calender_name)
        month = response.context[0]["periods"]['month']
        self.assertEqual((month.start, month.end),
                         (datetime.datetime(2000, 11, 1, 0, 0), datetime.datetime(2000, 12, 1, 0, 0)))

    def test_event_creation_anonymous_user(self):
        url = reverse("calendar_create_event",
                      kwargs={"calendar_slug": self.calender_slug})
        response = self.client.get(url, {})
        self.assertEqual(response.status_code, 302)

    def test_event_creation_admin_user(self):

        with self.login(self.user_admin.username, self.user_admin._unecrypted_password):

            url = reverse("calendar_create_event",
                          kwargs={"calendar_slug": self.calender_slug})
            response = self.client.get(url, {})
            self.assertEqual(response.status_code, 200)

            url = reverse("calendar_create_event",
                          kwargs={"calendar_slug": self.calender_slug})
            post_data = {'description': 'description', 'title': 'title',
                         'end_recurring_period_0': '2008-10-30', 'end_recurring_period_1': '10:22:00', 'end_recurring_period_2': 'AM',
                         'end_0': '2008-10-30', 'end_1': '10:22:00', 'end_2': 'AM',
                         'start_0': '2008-10-30', 'start_1': '09:21:57', 'start_2': 'AM'
                         }
            response = self.client.post(url, post_data)
            self.assertEqual(response.status_code, 302)

            url = reverse(
                "event", kwargs={"pk": 1, "calendar_slug": self.calender_slug})
            response = self.client.get(url, {})
            self.assertEqual(response.status_code, 200)

    def test_view_private_event(self):
        # attempting to view a private event should redirect anonymous users to login
        response = self.client.get(
            reverse("event", kwargs={"pk": 1, "calendar_slug": self.calender_slug}), {})
        self.assertEqual(response.status_code, 302)

    def test_delete_event_anonymous_user(self):
        # Only logged-in users should be able to delete, so we're redirected
        response = self.client.get(
            reverse("delete_event", kwargs={"calendar_slug": self.calender_slug, "pk": 1}), {})
        self.assertEqual(response.status_code, 302)

    def test_delete_event_admin_user(self):
        with self.login(self.user_admin.username, self.user_admin._unecrypted_password):
            event_dict = {'description': 'description',
                          'title': 'title',
                          'end_recurring_period': datetime.datetime(2008, 10, 30, 10, 22),
                          'end': datetime.datetime(2008, 10, 30, 10, 22),
                          'start': datetime.datetime(2008, 10, 30, 9, 21),
                          'calendar': self.calendar
                          }
            event = mommy.make('appointments.Event', **event_dict)
            # Load the deletion page

            response = self.client.get(
                reverse("delete_event", kwargs={"calendar_slug": self.calender_slug, "pk": event.id}), {})
            self.assertEqual(response.status_code, 200)

            # Delete the event
            response = self.client.post(
                reverse("delete_event", kwargs={"calendar_slug": self.calender_slug, "pk": event.id}), {})
            self.assertEqual(response.status_code, 302)

            # Since the event is now deleted, we get a 404
            response = self.client.get(
                reverse("delete_event", kwargs={"calendar_slug": self.calender_slug, "pk": event.id}), {})
            self.assertEqual(response.status_code, 404)
