from copy import deepcopy

from BTrees.OOBTree import OOBTree
from persistent.dict import PersistentDict
from persistent.list import PersistentList

from DateTime import DateTime
from zope.interface import implements
from zope.component import adapts
from zope.annotation.interfaces import IAnnotations

from plone.app.layout.navigation.interfaces import INavigationRoot

from ..interfaces import IDigestStorage
from .. import DigestMessageFactory as _


class BaseStorage(object):

    adapts(INavigationRoot)
    implements(IDigestStorage)

    key = NotImplemented
    label = NotImplemented

    def __init__(self, context):
        self.annotations = IAnnotations(context)

    def purge_now(self):
        raise NotImplementedError

    def store_activity(self, subscriber, activity_key, info):
        value = PersistentDict(**info)
        key = '%s-digest' % self.key
        if not key in self.annotations:
            self.annotations[key] = OOBTree()

        if not subscriber in self.annotations[key]:
            self.annotations[key][subscriber] = PersistentDict()

        if activity_key not in self.annotations[key][subscriber]:
             self.annotations[key][subscriber][activity_key] = PersistentList()

        self.annotations[key][subscriber][activity_key].append(value)

    def pop(self):
        """Gets
        """
        key = '%s-digest' % self.key
        self.annotations['%s-digest-last-purge' % key] = DateTime()
        if not key in self.annotations:
            return {}

        activity = deepcopy(self.annotations[key])
        self.annotations[key] = PersistentDict()
        return activity

    def last_purge(self):
        key = '%s-digest-last-purge' % self.key
        if not self.annotations.has_key(key):
            return None
        else:
            return self.annotations[key]

    def purge_user(self, subscriber):
        key = '%s-digest' % self.key
        if key in self.annotations:
            if subscriber in self.annotations[key]:
                del self.annotations[key][subscriber]


class DailyStorage(BaseStorage):

    key = 'daily'
    label = _("Daily")

    def purge_now(self):
        last_purge = self.last_purge()
        now = DateTime()
        if (not last_purge) or now - last_purge > 1 or now.day != last_purge.day:
            return True
        else:
            return False


class WeeklyStorage(BaseStorage):

    key = 'weekly'
    label = _("Weekly")

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


    def purge_now(self):
        last_purge = self.last_purge()
        now = DateTime()
        if (not last_purge) or now - last_purge > 30 or now.month != last_purge.month:
            return True
        else:
            return False


class ManualStorage(BaseStorage):

    key = 'manual'
    label = _("Automatic")

    def purge_now(self):
        return True
