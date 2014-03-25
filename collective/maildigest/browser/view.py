from zope.i18n import translate
from zope.interface import implements
from zope.component import getUtility

from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser import BrowserView
from plone import api

from collective.maildigest.interfaces import IDigestInfo, IDigestUtility
from collective.maildigest import DigestMessageFactory as _


class DigestInfo(BrowserView):

    implements(IDigestInfo)
    parent_subscribed = False

    def update(self):
        context = self.context
        utility = getUtility(IDigestUtility)
        user = api.user.get_current()
        user_id = user.getId()

        self.digest_delays = []
        subscribed_storage, recursive = utility.get_subscription(user_id, context, root=True)
        for name, storage in utility.get_storages(sort=True):
            self.digest_delays.append({
               'name': name,
               'selected': subscribed_storage and subscribed_storage.key == name,
               'label': _('${delay} email',
                          mapping={'delay': translate(storage.label,
                                                      context=self.request).lower()
                                   }),
                })

        self.recursive_subscription = recursive
        self.subscribed_nothing = not subscribed_storage

        if not subscribed_storage:
            parent_subscribed_storage, recursive = utility.get_subscription(user_id, context)
            if parent_subscribed_storage:
                self.parent_subscribed = True

class DigestSubscribe(BrowserView):

    def __call__(self):
        utility = getUtility(IDigestUtility)
        user = api.user.get_current()
        user_id = user.getId()
        subscription = self.request.get('digest-subscription')
        statusmessage = IStatusMessage(self.request)
        recursive = bool(self.request.get('digest-subscription-recursive', False))
        utility.switch_subscription(user_id, self.context, subscription, recursive)
        msg_type = 'info'
        if subscription is None:
            message = _("Please select daily or weekly digest.")
            msg_type = 'error'
        elif subscription == 'cancel-subscription':
            message = _("You cancelled your subscription to digest email about activity on this folder")
        else:
            storage = utility.get_storage(subscription)
            message = _('msg_subscribed_digest',
                        default="You subscribed to ${delay} digest email about activity on this folder",
                        mapping={'delay': translate(storage.label,
                                                    context=self.request).lower()})


        statusmessage.addStatusMessage(message, msg_type)
        return self.context.absolute_url()
