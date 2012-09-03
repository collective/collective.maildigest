from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase


class DigestIcon(ViewletBase):

    index = ViewPageTemplateFile('templates/container-digest-icon.pt')

    def update(self):
        super(DigestIcon, self).update()
        self.anonymous = self.portal_state.anonymous()
        if self.anonymous:
            return

        context, request = self.context, self.request
        self.digestinfo = context.unrestrictedTraverse('digestinfo')
        self.digestinfo.update()
        self.subscribed_daily = self.digestinfo.subscribed_daily
        self.subscribed_weekly = self.digestinfo.subscribed_weekly
        self.subscribed_nothing = self.digestinfo.subscribed_nothing
        self.form_url = "%s/digest-subscribe" % self.context.absolute_url()

