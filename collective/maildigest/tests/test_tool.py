import unittest2 as unittest
from zope.lifecycleevent import ObjectModifiedEvent
from zope.event import notify

from plone import api
from plone.app.testing.interfaces import TEST_USER_NAME, TEST_USER_ID
from plone.app.testing.helpers import login

from collective.maildigest.tests import base
from collective.maildigest.tool import get_tool


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
        self.subscriber = ('member', TEST_USER_NAME)

    def test_subscriptions(self):
        tool = get_tool()
        tool.switch_subscription(TEST_USER_NAME, self.workspace, 'daily')
        self.assertTrue(tool.get_subscription(TEST_USER_NAME, self.workspace)[0].key,
                        'daily')
        self.assertEqual(tool.get_subscribed(self.workspace, 'daily'),
                         (self.subscriber,))
        # not recursive
        self.assertFalse(tool.get_subscription(TEST_USER_NAME, self.folder)[0])

        # recursivity
        tool.switch_subscription(TEST_USER_NAME, self.workspace, 'daily', True)
        self.assertTrue(tool.get_subscription(TEST_USER_NAME, self.workspace)[0].key,
                        'daily')
        self.assertTrue(tool.get_subscription(TEST_USER_NAME, self.folder)[0].key,
                        'daily')
        self.assertEqual(tool.get_subscribed(self.workspace, 'daily'),
                         (self.subscriber,))
        self.assertEqual(tool.get_subscribed(self.folder, 'daily'),
                         (self.subscriber,))

        # activity storage
        tool.store_activity(self.workspace, 'add', **{'foo': 'bar'})
        storage = tool.get_storage('daily')
        activity_info = dict(storage.pop())
        self.assertEqual(activity_info.keys(), [self.subscriber])
        self.assertEqual(activity_info[self.subscriber].keys(), ['add'])
        self.assertEqual(activity_info[self.subscriber]['add'][0]['foo'], 'bar')
        self.assertEqual(activity_info[self.subscriber]['add'][0]['actor'],
                         TEST_USER_ID)

        testcontent = api.content.create(self.folder, 'Folder', 'test')
        storage = tool.get_storage('daily')
        activity_info = dict(storage.pop())
        self.assertEqual(activity_info.keys(), [self.subscriber])
        self.assertEqual(activity_info[self.subscriber].keys(), ['add'])
        self.assertEqual(activity_info[self.subscriber]['add'][0]['uid'],
                         testcontent.UID())
        self.assertEqual(activity_info[self.subscriber]['add'][0]['folder-uid'],
                         self.folder.UID())

    def test_switch_subscription(self):
        tool = get_tool()
        tool.switch_subscription(TEST_USER_NAME, self.workspace, 'daily')
        self.assertTrue(tool.get_subscription(TEST_USER_NAME, self.workspace)[0].key,
                        'daily')
        self.assertEqual(tool.get_subscribed(self.workspace, 'daily'),
                         (self.subscriber,))
        self.assertEqual(tool.get_subscribed(self.workspace, 'monthly'),
                         ())

        tool.switch_subscription(TEST_USER_NAME, self.workspace, 'monthly')
        self.assertTrue(tool.get_subscription(TEST_USER_NAME, self.workspace)[0].key,
                        'monthly')
        self.assertEqual(tool.get_subscribed(self.workspace, 'daily'),
                         ())
        self.assertEqual(tool.get_subscribed(self.workspace, 'monthly'),
                         (self.subscriber,))

        tool.switch_subscription(TEST_USER_NAME, self.workspace, '')
        self.assertEqual(tool.get_subscription(TEST_USER_NAME, self.workspace),
                         (None, None))
        self.assertEqual(tool.get_subscribed(self.workspace, 'daily'),
                         ())
        self.assertEqual(tool.get_subscribed(self.workspace, 'monthly'),
                         ())

    def test_activities(self):
        tool = get_tool()
        tool.switch_subscription(TEST_USER_NAME, self.workspace, 'daily', True)

        api.content.create(self.folder, 'Document', 'document')
        storage = tool.get_storage('daily')
        activity_info = dict(storage.pop())
        self.assertEqual(activity_info.keys(), [self.subscriber])
        self.assertEqual(activity_info[self.subscriber].keys(), ['add'])

        notify(ObjectModifiedEvent(self.folder.document))
        storage = tool.get_storage('daily')
        activity_info = dict(storage.pop())
        self.assertEqual(activity_info[self.subscriber].keys(), ['modify'])

        cb = self.folder.manage_cutObjects(['document'])
        self.workspace.manage_pasteObjects(cb)
        activity_info = dict(storage.pop())
        self.assertEqual(activity_info[self.subscriber].keys(), ['move'])

    def test_rules(self):
        from collective.maildigest.digestrules.rules import SameEditor,\
            AddedAndModifiedBySame, AddedAndRemoved, ModifiedAndRemoved,\
            Unauthorized
        tool = get_tool()
        subscriber = self.subscriber
        tool.switch_subscription(TEST_USER_NAME, self.workspace, 'daily', True)

        api.content.create(self.folder, 'Document', 'document')

        notify(ObjectModifiedEvent(self.folder.document))
        notify(ObjectModifiedEvent(self.folder.document))
        storage = tool.get_storage('daily')
        activity_info = dict(storage.pop())[subscriber]

        # unauthorized rule
        # api.content.transition(self.folder.document, 'private')
        # anonymous_info = Unauthorized()(self.portal, ('email', 'test'), activity_info)
        # self.assertNotIn('modify', anonymous_info)
        test_info = Unauthorized()(self.portal, subscriber, activity_info)
        self.assertEqual(len(test_info['modify']), 2)

        # same editor rule
        self.assertEqual(len(activity_info['modify']), 2)
        activity_info = SameEditor()(self.portal, subscriber, activity_info)
        self.assertEqual(len(activity_info['modify']), 1)

        # added and modified by same
        self.assertIn('modify', activity_info)
        activity_info = AddedAndModifiedBySame()(self.portal, subscriber, activity_info)
        self.assertNotIn('modify', activity_info)

        # modified and removed
        notify(ObjectModifiedEvent(self.folder.document))
        api.content.delete(self.folder.document)
        storage = tool.get_storage('daily')
        activity_info = dict(storage.pop())[subscriber]
        self.assertIn('delete', activity_info)
        self.assertIn('modify', activity_info)
        activity_info = ModifiedAndRemoved()(self.portal, subscriber, activity_info)
        self.assertNotIn('modify', activity_info)

        # added and removed
        api.content.create(self.folder, 'Document', 'document2')
        api.content.create(self.folder, 'Document', 'document3')
        api.content.delete(self.folder.document2)
        storage = tool.get_storage('daily')
        activity_info = dict(storage.pop())[subscriber]
        self.assertEqual(len(activity_info['add']), 2)
        activity_info = AddedAndRemoved()(self.portal, subscriber, activity_info)
        self.assertEqual(len(activity_info['add']), 1)
        self.assertNotIn('delete', activity_info)

    def test_purge_user(self):
        tool = get_tool()
        tool.switch_subscription(TEST_USER_NAME, self.workspace, 'daily', True)
        api.content.create(self.folder, 'Document', 'document')
        tool.switch_subscription(TEST_USER_NAME, self.workspace, '', True)
        storage = tool.get_storage('daily')
        activity_infos = dict(storage.pop())
        self.assertNotIn(self.subscriber, activity_infos)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)