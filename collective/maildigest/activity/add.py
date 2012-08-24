from zope.component import getUtility

from ..interfaces import IDigestUtility
from plone.uuid.interfaces import IUUID, IUUIDAware

def store_activity(document, event):
    if not IUUIDAware.providedBy(document):
        return

    if document.isTemporary():
        return

    folder = document.aq_parent
    utility = getUtility(IDigestUtility).store_activity(folder,
                                                        'add',
                                                        uid=IUUID(document))
