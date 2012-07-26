from zope.interface import implements
from zope.component import queryUtility, getUtility

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from collective.subscribe.interfaces import ISubscriptionCatalog, IUIDStrategy
from collective.subscribe.interfaces import ISubscribers
from collective.subscribe.subscriber import ItemSubscriber

from ..interfaces import IDigestInfo, IDigestUtility
from Products.statusmessages.interfaces import IStatusMessage
from .. import DigestMessageFactory as _


class DigestInfo(BrowserView):

    implements(IDigestInfo)

    def update(self):
        context = self.context
        mtool = getToolByName(context, 'portal_membership')
        self.uid = IUIDStrategy(context).getuid()
        self.container = queryUtility(ISubscribers)
        self.utility = getUtility(IDigestUtility)
        self.catalog = queryUtility(ISubscriptionCatalog)
        self.user = mtool.getAuthenticatedMember()
        self.user_id = self.user.getId()

        self.subscriber = ItemSubscriber(user=self.user_id)
        self.subscribed_daily = ('member', self.user_id) in self.catalog.search({'daily-digest': self.uid})
        self.subscribed_weekly = ('member', self.user_id) in self.catalog.search({'weekly-digest': self.uid})
        self.subscribed_nothing = not (self.subscribed_daily or self.subscribed_weekly)


class DigestSubscribe(DigestInfo):

    def __call__(self):
        self.update()
        subscription = self.request.get('digest-subscription')
        statusmessage = IStatusMessage(self.request)
        self.utility.switch_subscription(self.subscriber, self.context, subscription)
        msg_type = 'info'
        if subscription is None:
            message = _("Please select daily or weekly digest.")
            msg_type = 'error'
        elif subscription == 'daily-digest':
            message = _("You subscribed to daily digest email about activity on this folder")
        elif subscription == 'weekly-digest':
            message = _("You subscribed to weekly digest email about activity on this folder")
        elif subscription == 'cancel-subscription':
            message = _("You cancelled your subscription to digest email about activity on this folder")
        else:
            raise ValueError

        statusmessage.addStatusMessage(message, msg_type)
        return self.context.absolute_url()
