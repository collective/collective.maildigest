from copy import deepcopy

from BTrees.OOBTree import OOBTree
from persistent.dict import PersistentDict
from persistent.list import PersistentList

from DateTime import DateTime
from zope.interface import implements
from zope.component import adapts
from zope.annotation.interfaces import IAnnotations

from plone.app.layout.navigation.interfaces import INavigationRoot

from collective.maildigest.interfaces import IDigestStorage
from collective.maildigest import DigestMessageFactory as _
from collective.maildigest.tool import STORAGE_KEY_PREFIX


class BaseStorage(object):

    adapts(INavigationRoot)
    implements(IDigestStorage)

    key = NotImplemented
    label = NotImplemented
    icon = 'maildigest-weekly.png'

    def __init__(self, context):
        self.annotations = IAnnotations(context)

    def _get_key(self):
        return '%s.%s' % (STORAGE_KEY_PREFIX, self.key)

    def _get_activities(self):
        key = self._get_key()
        if key not in self.annotations:
            self.annotations[key] = OOBTree()

        return self.annotations[key]

    def _set_activities(self, infos):
        key = self._get_key()
        if key not in self.annotations:
            self.annotations[key] = OOBTree()

        self.annotations[key] = infos

    def purge_now(self):
        raise NotImplementedError

    def store_activity(self, subscriber, activity_key, info):
        """Store an activity for a subscriber
        @param subscriber: (str - namespace, str - user id)
        @param activity_key: str - id of type of activity ('add', 'delete', etc)
        @param info: dict - information about activity
        """
        value = PersistentDict(**info)
        key = self._get_key()

        activities = self._get_activities()
        if subscriber not in self.annotations[key]:
            activities[subscriber] = PersistentDict()

        if activity_key not in self.annotations[key][subscriber]:
            activities[subscriber][activity_key] = PersistentList()

        activities[subscriber][activity_key].append(value)

    def _set_lastpurge(self, date):
        key = self._get_key()
        self.annotations[key + '.lastpurge'] = date

    def pop(self):
        """Get all activities and purge them
        """
        self._set_lastpurge(DateTime())
        activity = deepcopy(self._get_activities())
        self._set_activities(OOBTree())
        return activity

    def last_purge(self):
        """Get date of last purge
        """
        key = self._get_key()
        if key + '.lastpurge' not in self.annotations:
            return None
        else:
            return self.annotations[key + '.lastpurge']

    def purge_user(self, subscriber):
        """Remove activities subscribed for this user
        @param subscriber: (str - namespace, str - user id)
        """
        if subscriber in self._get_activities():
            del self._get_activities()[subscriber]


class DailyStorage(BaseStorage):

    key = 'daily'
    label = _("Daily")
    icon = 'maildigest-daily.png'
    frequency = 24

    def purge_now(self):
        last_purge = self.last_purge()
        now = DateTime()
        if (not last_purge) or now - last_purge > 1 or now.day() != last_purge.day():
            return True
        else:
            return False


class WeeklyStorage(BaseStorage):

    key = 'weekly'
    label = _("Weekly")
    frequency = 24 * 7

    def purge_now(self):
        now = DateTime()
        if now.DayOfWeek() != 'Monday':
            return False

        last_purge = self.last_purge()
        if (not last_purge) or now - last_purge > 1:
            return True
        else:
            return False


class MonthlyStorage(BaseStorage):

    key = 'monthly'
    label = _("Monthly")
    frequency = 24 * 31

    def purge_now(self):
        last_purge = self.last_purge()
        now = DateTime()
        if (not last_purge) or now - last_purge > 30 or now.month() != last_purge.month():
            return True
        else:
            return False


class ManualStorage(BaseStorage):

    key = 'manual'
    label = _("Automatic")
    frequency = 0

    def purge_now(self):
        return True
