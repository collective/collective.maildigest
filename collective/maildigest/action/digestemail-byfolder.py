from copy import deepcopy

from zope.i18n import translate
from zope.component import getUtility

from Products.MailHost.interfaces import IMailHost
from Products.MailHost.MailHost import formataddr
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from .. import DigestMessageFactory as _
from . import BaseAction


class DigestEmailMessage(BrowserView):

    def folders(self):
        """sort digest by folders
        """
        ctool = getToolByName(self.context, 'portal_catalog')
        toLocTime = self.context.unrestrictedTraverse('@@plone').toLocalizedTime
        folders = {}

        for activity, activity_infos in self.info.items():
            for info in activity_infos:
                folder_uid = info['folder-uid']
                if folder_uid not in folders:
                    if not folder_uid in folders:
                        folder_brain = ctool.unrestrictedSearchResults(UID=info['folder-uid'])
                        if len(folder_brain) < 1:
                            continue
                        folder_brain = folder_brain[0]
                        folder_uid = info['folder-uid']
                        folders[folder_uid] = {'title': folder_brain.Title,
                                               'url': folder_brain.getURL()}

                doc_brain = ctool.unrestrictedSearchResults(UID=info['uid'])
                if not doc_brain:
                    doc_info = {'title': info.get('title', ''),
                                'actor': info['actor_fullname'],
                                'date': toLocTime(info['date'])}
                else:
                    doc_brain = doc_brain[0]
                    doc_info = {'title': doc_brain.Title or doc_brain.getId,
                                'url': doc_brain.getURL(),
                                'actor': info['actor_fullname'],
                                'date': toLocTime(info['date'])}

                folders[folder_uid].setdefault(activity, []).append(doc_info)

        folders = folders.values()
        folders.sort(key=lambda x: x['url'])
        return folders


class DigestEmail(BaseAction):

    def execute(self, portal, storage, subscriber, info):
        mailhost = getUtility(IMailHost)

        site_language = portal.portal_properties.site_properties.getProperty('default_language')
        user_type, user_value = subscriber
        if user_type == 'email':
            mto = user_value
            target_language = site_language
        elif user_type == 'member':
            user = portal.portal_membership.getMemberById(user_value)
            target_language = user.getProperty('language', None) or site_language
            mto = user.getProperty('email', None)
            if not mto:
                return

        subject = "[%s] %s" % (portal.Title(),
                               translate(_("${storage} activity digest",
            mapping={'storage': storage.label}),
            target_language=target_language))

        mfrom = formataddr((portal.email_from_name, portal.email_from_address))

        message_view = portal.unrestrictedTraverse('digestemail-byfolder')
        message_view.info = deepcopy(info)
        message_view.user_type = user_type
        message_view.user_value = user_value
        html = message_view().strip()

        if html:
            mailhost.send(html, mto=mto, mfrom=mfrom, subject=subject,
                          charset='utf-8', msg_type='text/html')
