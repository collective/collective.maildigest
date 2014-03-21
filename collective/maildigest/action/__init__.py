from zope.interface import implements

from collective.maildigest.interfaces import IDigestAction

class BaseAction(object):

    implements(IDigestAction)

    def __call__(self, *args, **kwargs):
        return self.execute(*args, **kwargs)