import unittest2 as unittest
from collective.maildigest.tests import base
from plone import api
from collective.maildigest.tool import get_tool
from plone.app.testing.interfaces import TEST_USER_NAME, TEST_USER_ID
from plone.app.testing.helpers import login


class TestTool(base.IntegrationTestCase):
    """We tests the setup (install) of the addons. You should check all
    stuff in profile are well activated (browserlayer, js, content types, ...)
    """

    def setUp(self):
        super(TestTool, self).setUp()
        self.portal = self.layer['portal']
        login(self.portal, TEST_USER_NAME)
        self.workspace = api.content.create(self.portal, 'Folder', 'Workspace')
        self.folder = api.content.create(self.workspace, 'Folder', 'folder')

    def test_subscriptions(self):
        tool = get_tool()
        tool.switch_subscription(TEST_USER_NAME, self.workspace, 'daily')
        self.assertTrue(tool.get_subscription(TEST_USER_NAME, self.workspace)[0].key,
                        'daily')
        self.assertEqual(tool.get_subscribed(self.workspace, 'daily'),
                         (('member', TEST_USER_NAME),))
        # not recursive
        self.assertFalse(tool.get_subscription(TEST_USER_NAME, self.folder)[0])

        # recursivity
        tool.switch_subscription(TEST_USER_NAME, self.workspace, 'daily', True)
        self.assertTrue(tool.get_subscription(TEST_USER_NAME, self.workspace)[0].key,
                        'daily')
        self.assertTrue(tool.get_subscription(TEST_USER_NAME, self.folder)[0].key,
                        'daily')
        self.assertEqual(tool.get_subscribed(self.workspace, 'daily'),
                         (('member', TEST_USER_NAME),))
        self.assertEqual(tool.get_subscribed(self.folder, 'daily'),
                         (('member', TEST_USER_NAME),))

        # activity storage
        tool.store_activity(self.workspace, 'add', **{'foo': 'bar'})
        storage = tool.get_storage('daily')
        activity_info = dict(storage.pop())
        self.assertEqual(activity_info.keys(), [('member', 'test-user')])
        self.assertEqual(activity_info[('member', 'test-user')].keys(), ['add'])
        self.assertEqual(activity_info[('member', 'test-user')]['add'][0]['foo'], 'bar')
        self.assertEqual(activity_info[('member', 'test-user')]['add'][0]['actor'],
                         TEST_USER_ID)

        testcontent = api.content.create(self.folder, 'Folder', 'test')
        storage = tool.get_storage('daily')
        activity_info = dict(storage.pop())
        self.assertEqual(activity_info.keys(), [('member', 'test-user')])
        self.assertEqual(activity_info[('member', 'test-user')].keys(), ['add'])
        self.assertEqual(activity_info[('member', 'test-user')]['add'][0]['uid'],
                         testcontent.UID())
        self.assertEqual(activity_info[('member', 'test-user')]['add'][0]['folder-uid'],
                         self.folder.UID())


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)