from plone.uuid.interfaces import IUUID, IUUIDAware

from collective.maildigest.browser.interfaces import ILayer
from collective.maildigest.tool import get_tool


def store_activity(document, event):
    if not ILayer.providedBy(getattr(document, 'REQUEST', None)):
        return

    if not IUUIDAware.providedBy(document):
        return

    folder = document.aq_parent
    get_tool().store_activity(folder, 'modify', uid=IUUID(document))
