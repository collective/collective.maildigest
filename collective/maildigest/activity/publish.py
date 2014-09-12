from Acquisition import aq_parent

from plone.uuid.interfaces import IUUID, IUUIDAware
from collective.maildigest.browser.interfaces import ILayer
from collective.maildigest.tool import get_tool
from plone import api

PUBLISHED_STATES = ['published']  # patch this if necessary

def store_activity(document, event):
    if not ILayer.providedBy(getattr(document, 'REQUEST', None)):
        return
    elif not IUUIDAware.providedBy(document):
        return
    elif api.content.get_state(document) not in PUBLISHED_STATES:
        return

    folder = aq_parent(document)
    if not folder:
        return

    get_tool().store_activity(folder, 'publish', uid=IUUID(document))
