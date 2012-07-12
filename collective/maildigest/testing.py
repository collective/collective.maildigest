from plone.testing import z2

from plone.app.testing import *
import collective.maildigest

FIXTURE = PloneWithPackageLayer(zcml_filename="configure.zcml",
                                zcml_package=collective.maildigest,
                                additional_z2_products=[],
                                gs_profile_id='collective.maildigest:default',
                                name="collective.maildigest:FIXTURE")

INTEGRATION = IntegrationTesting(bases=(FIXTURE,),
                        name="collective.maildigest:Integration")

FUNCTIONAL = FunctionalTesting(bases=(FIXTURE,),
                        name="collective.maildigest:Functional")

