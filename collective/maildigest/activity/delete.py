from zope.component import getUtility

from ..interfaces import IDigestUtility
from plone.uuid.interfaces import IUUID, IUUIDAware

def store_activity(document, event):
    if not IUUIDAware.providedBy(document):
        return

    folder = document.aq_parent
    utility = getUtility(IDigestUtility).store_activity(folder,
                                                        'delete',
                                                        title=document.title_or_id(),
                                                        uid=IUUID(document))
