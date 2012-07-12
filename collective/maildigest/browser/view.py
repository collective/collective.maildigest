from zope.interface import implements
from zope.component import queryUtility, getUtility, getMultiAdapter
from zope.component.interfaces import ComponentLookupError

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

from collective.inviting.interfaces import IContentSubscribers
from collective.subscribe.interfaces import ISubscriptionCatalog, IUIDStrategy
from collective.subscribe.interfaces import ISubscribers, ISubscriptionKeys
from collective.subscribe.subscriber import ItemSubscriber

from ..interfaces import IDigestInfo
from Products.statusmessages.interfaces import IStatusMessage
from .. import DigestMessageFactory as _


class DigestInfo(BrowserView):

    implements(IDigestInfo)

    def update(self):
        context = self.context
        mtool = getToolByName(context, 'portal_membership')
        self.uid = IUIDStrategy(context).getuid()
        self.contentsubscriber = IContentSubscribers(context)
        self.container = queryUtility(ISubscribers)
        self.catalog = queryUtility(ISubscriptionCatalog)
        self.user = mtool.getAuthenticatedMember()
        self.user_id = self.user.getId()
        self.subscriber = ItemSubscriber(user=self.user_id)
        self.subscribed_daily = len(self.catalog.search({'daily-digest': self.uid, 'member': self.user_id})) == 1
        self.subscribed_weekly = len(self.catalog.search({'weekly-digest': self.uid, 'member': self.user_id})) == 1
        self.subscribed_nothing = not (self.subscribed_daily or self.subscribed_weekly)


class DigestSubscribe(DigestInfo):

    def __call__(self):
        self.update()
        subscription = self.request['digest-subscription']
        statusmessage = IStatusMessage(self.request)
        if subscription == 'daily-digest':
            self.catalog.unindex(self.subscriber, self.uid, 'weekly-digest')
            self.catalog.index(self.subscriber, self.uid, 'daily-digest')
            message = _("You subscribed to daily digest email about activity on this folder")
        elif subscription == 'weekly-digest':
            self.catalog.unindex(self.subscriber, self.uid, 'daily-digest')
            self.catalog.index(self.subscriber, self.uid, 'weekly-digest')
            message = _("You subscribed to weekly digest email about activity on this folder")
        elif subscription == 'cancel-subscription':
            self.catalog.unindex(self.subscriber, self.uid, 'daily-digest')
            self.catalog.unindex(self.subscriber, self.uid, 'weekly-digest')
            message = _("You cancelled your subscription to digest email about activity on this folder")
        else:
            raise ValueError

        statusmessage.addStatusMessage(message, 'info')
        return self.context.absolute_url()