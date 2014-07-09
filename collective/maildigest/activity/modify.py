from Products.Archetypes.interfaces import IObjectInitializedEvent
from plone.uuid.interfaces import IUUID, IUUIDAware


from collective.maildigest.browser.interfaces import ILayer
from collective.maildigest.tool import get_tool
from zope.container.interfaces import IContainerModifiedEvent


def store_activity(document, event):
    if IObjectInitializedEvent.providedBy(event):
        return
    elif IContainerModifiedEvent.providedBy(event):
        return
    elif not ILayer.providedBy(getattr(document, 'REQUEST', None)):
        return
    elif not IUUIDAware.providedBy(document):
        return

    folder = document.aq_parent
    get_tool().store_activity(folder, 'modify', uid=IUUID(document))
