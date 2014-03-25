from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone import api

from collective.maildigest import DigestMessageFactory as _
from collective.maildigest.tool import get_tool
from zope.i18n import translate


class DigestIcon(ViewletBase):

    index = ViewPageTemplateFile('templates/container-digest-icon.pt')

    def update(self):
        super(DigestIcon, self).update()
        self.anonymous = self.portal_state.anonymous()
        if self.anonymous:
            return

        user_id = api.user.get_current().getId()
        utility = get_tool()
        storage, recursive = utility.get_subscription(user_id, self.context)
        if not storage:
            self.icon = 'maildigest.png'
            if recursive:
                self.title = _('folder_digesticon_title_recursive',
                               default=u"Subscribe to recurring digest of activity in this folder and all its subfolders")
            else:
                self.title = _('folder_digesticon_title',
                               default=u"Subscribe to recurring digest of activity in this folder")

        else:
            self.icon = storage.icon
            if recursive:
                self.title = _('title_digesticon_recursives',
                               default=u"You have subscribed to ${delay} digest on this folder and all its subfolders",
                               mapping={'delay': translate(storage.label, context=self.request).lower()})
            else:
                self.title = _('title_digesticon',
                               default=u"You have subscribed to ${delay} digest on this folder",
                               mapping={'delay': translate(storage.label, context=self.request).lower()})

        self.form_url = "%s/digest-subscribe" % self.context.absolute_url()
