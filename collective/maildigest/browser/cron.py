from zope.component import getUtility

from Products.Five.browser import BrowserView

from ..interfaces import IDigestUtility


class DigestCron(BrowserView):

    def __call__(self):
        getUtility(IDigestUtility).check_digests_to_purge_and_apply(self.context)
