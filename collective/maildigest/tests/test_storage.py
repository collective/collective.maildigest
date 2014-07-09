from DateTime.DateTime import DateTime
from collective.maildigest.tests import base
from collective.maildigest.tool import get_tool


class TestStorage(base.IntegrationTestCase):
    """We tests the setup (install) of the addons. You should check all
    stuff in profile are well activated (browserlayer, js, content types, ...)
    """

    def test_storage(self):
        tool = get_tool()
        daily_storage = tool.get_storage('daily')
        daily_storage._set_lastpurge(DateTime())
        self.assertFalse(daily_storage.purge_now())
        daily_storage._set_lastpurge(DateTime() - 2)
        self.assertTrue(daily_storage.purge_now())
        daily_storage.pop()
        self.assertFalse(daily_storage.purge_now())

        weekly_storage = tool.get_storage('weekly')
        weekly_storage._set_lastpurge(DateTime())
        self.assertFalse(weekly_storage.purge_now())
        weekly_storage._set_lastpurge(DateTime() - 8)
        if DateTime().DayOfWeek() == 'Monday':
            self.assertTrue(weekly_storage.purge_now())
        else:
            self.assertFalse(weekly_storage.purge_now())

        monthly_storage = tool.get_storage('monthly')
        monthly_storage._set_lastpurge(DateTime())
        self.assertFalse(monthly_storage.purge_now())
        monthly_storage._set_lastpurge(DateTime() - 40)
        self.assertTrue(monthly_storage.purge_now())