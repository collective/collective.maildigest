import unittest2 as unittest

from plone import api
from plone.app.testing.interfaces import TEST_USER_NAME
from plone.app.testing.helpers import login

from collective.maildigest.tests import base
from collective.maildigest.browser.viewlet import DigestIcon


class TestViews(base.IntegrationTestCase):
    """We tests the setup (install) of the addons. You should check all
    stuff in profile are well activated (browserlayer, js, content types, ...)
    """

    def setUp(self):
        super(TestViews, self).setUp()
        self.portal = self.layer['portal']
        login(self.portal, TEST_USER_NAME)
        self.workspace = api.content.create(self.portal, 'Folder', 'Workspace')
        self.folder = api.content.create(self.workspace, 'Folder', 'folder')

    def test_view(self):
        portal = self.portal
        workspace = self.workspace
        view = workspace.unrestrictedTraverse('@@digest-subscribe')
        viewlet = DigestIcon(workspace.folder, workspace.REQUEST, None, None)

        view.update()
        self.assertTrue(view.subscribed_nothing)

        viewlet.update()
        self.assertEqual(viewlet.icon, 'maildigest.png')

        portal.REQUEST['digest-subscription'] = 'daily'
        portal.REQUEST['digest-subscription-recursive'] = True
        workspace.unrestrictedTraverse('@@digest-subscribe-submit')()

        view.update()
        self.assertFalse(view.subscribed_nothing)
        self.assertTrue(view.recursive_subscription)
        self.assertEqual(view.digest_delays[0]['name'], 'daily')
        self.assertTrue(view.digest_delays[0]['selected'])

        viewlet = DigestIcon(workspace, workspace.REQUEST, None, None)
        viewlet.update()
        self.assertEqual(viewlet.icon, 'maildigest-daily.png')

        viewlet.update()
        self.assertEqual(viewlet.icon, 'maildigest-daily.png')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)