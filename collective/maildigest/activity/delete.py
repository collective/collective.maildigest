from zope.component import getUtility

from plone.uuid.interfaces import IUUID, IUUIDAware

from collective.maildigest.interfaces import IDigestUtility
from collective.maildigest.browser.interfaces import ILayer


def store_activity(document, event):
    if not ILayer.providedBy(getattr(document, 'REQUEST', None)):
        return

    if not IUUIDAware.providedBy(document):
        return

    folder = document.aq_parent
    getUtility(IDigestUtility).store_activity(folder, 'delete',
                                              title=document.title_or_id(),
                                              uid=IUUID(document))
