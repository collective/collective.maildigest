from Acquisition import aq_parent

from plone.uuid.interfaces import IUUID, IUUIDAware
from collective.maildigest.browser.interfaces import ILayer
from collective.maildigest.tool import get_tool


def store_activity(document, event):
    if not event.oldParent:
        # this is not a move, this is an adding
        return

    if not ILayer.providedBy(getattr(document, 'REQUEST', None)):
        return

    if not IUUIDAware.providedBy(document):
        return

    if event.oldParent == event.newParent:
        # ignore renames
        return

    folder = aq_parent(document)
    if not folder:
        return

    get_tool().store_activity(folder, 'move', uid=IUUID(document),
                              old_parent=IUUID(event.oldParent))
