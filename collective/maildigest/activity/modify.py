from zope.component import getUtility

from ..interfaces import IDigestUtility
from plone.uuid.interfaces import IUUID

def store_activity(document, event):
    folder = document.aq_parent
    utility = getUtility(IDigestUtility).store_activity(folder,
                                                        'modify',
                                                        uid=IUUID(document))
