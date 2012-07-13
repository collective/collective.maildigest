from zope.component import getAdapters, queryUtility
from DateTime import DateTime

from Products.CMFCore.utils import getToolByName

from collective.subscribe.interfaces import ISubscriptionCatalog, IUIDStrategy

from .interfaces import IDigestStorage


class DigestUtility(object):

    def store_activity(self, folder, activity_key, **info):
        if 'date' not in info:
            info['date'] = DateTime()

        if 'actor' not in info:
            user = getToolByName(folder, 'portal_membership').getAuthenticatedMember()
            info['actor'] = user.getId()

        site = getToolByName(folder, 'portal_url').getPortalObject()
        catalog = queryUtility(ISubscriptionCatalog)
        storages = getAdapters((site,), IDigestStorage)
        uid = IUIDStrategy(folder)()
        for key, storage in storages:
            subscribers = catalog.search({'%s-digest' % key: uid})
            for k, v in subscribers:
                storage.store_activity(v, activity_key, info)
