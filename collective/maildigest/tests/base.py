import unittest2 as unittest
import transaction
from zope.interface import alsoProvides
from plone.app import testing

from collective.maildigest.testing import INTEGRATION, FUNCTIONAL
from collective.maildigest.browser.interfaces import ILayer


class UnitTestCase(unittest.TestCase):

    def setUp(self):
        pass

class IntegrationTestCase(unittest.TestCase):

    layer = INTEGRATION

    def setUp(self):
        super(unittest.TestCase, self).setUp()
        self.portal = self.layer['portal']
        alsoProvides(self.portal.REQUEST, ILayer)
        testing.setRoles(self.portal, testing.TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')


class FunctionalTestCase(IntegrationTestCase):

    layer = FUNCTIONAL

    def setUp(self):
        #we must commit the transaction
        transaction.commit()
