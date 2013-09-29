import datetime

from django.test import TestCase

from appointments.templatetags import appointments_tags


class TestTemplateTags(TestCase):

    def test_querystring_for_datetime(self):
        date = datetime.datetime(2008, 1, 1, 0, 0, 0)
        query_string = appointments_tags.querystring_for_date(date)
        self.assertEqual("?year=2008&month=1&day=1&hour=0&minute=0&second=0",
                         query_string)
