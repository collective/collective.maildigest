from zope.lifecycleevent import ObjectModifiedEvent
from zope.event import notify

from plone import api
from plone.app.testing.interfaces import TEST_USER_NAME, TEST_USER_ID
from plone.app.testing.helpers import login

from collective.maildigest.tests import base
from collective.maildigest.tool import get_tool
from collective.maildigest.interfaces import IDigestAction
from zope.component._api import getUtility


class TestActions(base.IntegrationTestCase):
    """We tests the setup (install) of the addons. You should check all
    stuff in profile are well activated (browserlayer, js, content types, ...)
    """

    def setUp(self):
        super(TestActions, self).setUp()
        portal = self.portal = self.layer['portal']
        login(portal, TEST_USER_NAME)
        self.workspace = api.content.create(portal, 'Folder', 'Workspace')
        self.folder = api.content.create(self.workspace, 'Folder', 'folder')
        api.user.get(TEST_USER_ID).setProperties({'email': 'test-user@example.com'})
        portal.email_from_name, portal.email_from_address = 'Test site', 'webmaster@example.com'

    def test_digestemail_by_folder(self):
        tool = get_tool()
        tool.switch_subscription(TEST_USER_ID, self.workspace, 'daily', True)

        api.content.create(self.folder, 'Document', 'document')
        notify(ObjectModifiedEvent(self.folder.document))
        cb = self.folder.manage_cutObjects(['document'])
        self.workspace.manage_pasteObjects(cb)
        storage = tool.get_storage('daily')
        activity_info = dict(storage.pop())
        subscriber = ('member', TEST_USER_ID)
        message_view = self.portal.unrestrictedTraverse('digestemail-byfolder')
        message_view.info = activity_info[subscriber]
        message_view.user_type, message_view.user_value = subscriber

        from bs4 import BeautifulSoup
        html = message_view()
        soup = BeautifulSoup(html)

        self.assertEqual([e.text.strip() for e in soup.find_all('h3')],
                         [u'Items moved into the folder',
                          u'New items',
                          u'Modified items'])

        # @TODO: mock mail host to actually test
        email_action = getUtility(IDigestAction, name='digestemail-byfolder')
        email_action(self.portal, storage, subscriber, activity_info[subscriber])

    def test_purge_and_apply(self):
        tool = get_tool()
        tool.switch_subscription(TEST_USER_ID, self.workspace, 'daily', True)

        api.content.create(self.folder, 'Document', 'document')
        notify(ObjectModifiedEvent(self.folder.document))
        cb = self.folder.manage_cutObjects(['document'])
        self.workspace.manage_pasteObjects(cb)

        # @TODO: mock mail host to actually test
        tool.check_digests_to_purge_and_apply()