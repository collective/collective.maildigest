from BTrees.OOBTree import OOBTree
from persistent.dict import PersistentDict
from persistent.list import PersistentList

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

    def store_activity(self, userid, activity_key, info):
        value = PersistentDict(**info)
        key = 'digest-%s' % self.key
        if not key in self.annotations:
            self.annotations[key] = OOBTree()

        if not userid in self.annotations[key]:
            self.annotations[key][userid] = PersistentDict()

        if activity_key not in self.annotations[key][userid]:
             self.annotations[key][userid][activity_key] = PersistentList()

        self.annotations[key][userid][activity_key].append(value)


class DailyStorage(BaseStorage):

    key = 'daily'
    label = _("Daily email")


class WeeklyStorage(BaseStorage):

    key = 'weekly'
    label = _("Weekly email")


class MonthlyStorage(BaseStorage):

    key = 'monthly'
    label = _("Monthly email")