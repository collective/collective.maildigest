from Acquisition import aq_parent
from zope.component import getUtility

from plone.uuid.interfaces import IUUID, IUUIDAware
from collective.maildigest.browser.interfaces import ILayer
from collective.maildigest.interfaces import IDigestUtility


def store_activity(document, event):
    if not ILayer.providedBy(getattr(document, 'REQUEST', None)):
        return

    if not IUUIDAware.providedBy(document):
        return

    if document.isTemporary():
        return

    folder = aq_parent(document)
    if not folder:
        return

    getUtility(IDigestUtility).store_activity(folder, 'add',
                                              uid=IUUID(document))
