from DateTime import DateTime
from zope.component import getAdapters, getAdapter
from zope.component import getUtility
from zope.component import queryUtility, getUtilitiesFor

from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone import api

from collective.subscribe.interfaces import ISubscriptionCatalog, IUIDStrategy
from collective.subscribe.subscriber import ItemSubscriber

from collective.maildigest.interfaces import IDigestStorage, IDigestAction, IDigestFilterRule,\
    IDigestUtility

STORAGE_KEY_PREFIX = 'collective.maildigest.storage'


class DigestUtility(object):

    def _get_catalog(self):
        if not hasattr(self, '_catalog'):
            self._catalog = queryUtility(ISubscriptionCatalog)
        return self._catalog

    def _get_key(self, storage_id):
        return '%s.%s' % (STORAGE_KEY_PREFIX, storage_id)

    def _get_uid(self, content):
        if IPloneSiteRoot.providedBy(content):
            return 'plonesite'
        else:
            return IUIDStrategy(content)()

    def get_storages(self, sort=False):
        """Get all storages
        @return list of tuples: name, object
        """
        storages = getAdapters((api.portal.get(),), IDigestStorage)
        if sort:
            storages = list(storages)
            storages.sort(key=lambda s: s[1].frequency)

        return storages

    def get_storage(self, storage_id):
        """Get storage by id
        @return object
        """
        return getAdapter(api.portal.get(), IDigestStorage, name=storage_id)

    def store_activity(self, folder, activity_key, **info):
        """Get activity info on a folder and stores it in activity storages
        """
        if 'date' not in info:
            info['date'] = DateTime()

        if 'actor' not in info:
            user = api.portal.get_tool('portal_membership').getAuthenticatedMember()
            info['actor'] = user.getId()
            info['actor_fullname'] = user.getProperty('fullname', '') or info['actor']

        catalog = self._get_catalog()
        uid = self._get_uid(folder)
        info['folder-uid'] = uid
        for storage_id, storage in self.get_storages():
            subscribers = catalog.search({self._get_key(storage_id): uid})
            for subscriber in subscribers:
                storage.store_activity(subscriber, activity_key, info)

    def check_digests_to_purge_and_apply(self, debug=False):
        """Check for each storage if it has to be purged and applied, and apply
        """
        site = api.portal.get()
        for storage in self.get_storages():
            storage = storage[1]
            if debug or storage.purge_now():
                digest_info = storage.pop()
                self._apply_digest(site, storage, digest_info)

    def _apply_digest(self, site, storage, digest_info):
        """Filter digest info using registered filters
           apply registered strategies for user with filtered info
        """
        filter_rules = [r[1] for r in getUtilitiesFor(IDigestFilterRule)]
        digest_strategies = [r[1] for r in getUtilitiesFor(IDigestAction)]

        for subscriber, info in digest_info.items():
            for rule in filter_rules:
                info = rule(site, subscriber, info)

            for action in digest_strategies:
                action(site, storage, subscriber, info)

    def switch_subscription(self, user_id, folder, storage_id):
        """Change the subscription of the subscriber on the folder
            @param user_id: str - user id
            @param folder: object
            @param storage_id: str
        """
        subscriber = ItemSubscriber(user=user_id)
        catalog = self._get_catalog()
        uid = self._get_uid(folder)
        for name, storage in self.get_storages():
            if name == storage_id:
                catalog.index(subscriber, uid, self._get_key(name))
            else:
                storage.purge_user(subscriber)
                catalog.unindex(subscriber, uid, self._get_key(name))

    def get_subscription(self, user_id, folder):
        """Get the id of the storage selected by the subscriber on the folder
            @param user_id: str - user id
            @param folder: object
            @return storage: object - IDigestStorage utility
        """
        uid = self._get_uid(folder)
        catalog = self._get_catalog()
        for storage_id, storage in self.get_storages():
            storage_key = self._get_key(storage_id)
            if ('member', user_id) in catalog.search({storage_key: uid}):
                return storage
        else:
            return None

def get_tool():
    return getUtility(IDigestUtility)