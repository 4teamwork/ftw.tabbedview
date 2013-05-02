from ftw.testing.layer import ComponentRegistryLayer
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from z3c.autoinclude.api import disable_dependencies
from z3c.autoinclude.api import disable_plugins
from zope.configuration import xmlconfig


class ZCMLLayer(ComponentRegistryLayer):
    """Loads the zcml of ftw.tabbedview and dependencies.
    """

    def setUp(self):
        disable_dependencies()
        disable_plugins()

        super(ZCMLLayer, self).setUp()

        import ftw.tabbedview.tests
        self.load_zcml_file('tests.zcml', ftw.tabbedview.tests)

        import plone.registry
        self.load_zcml_file('configure.zcml', plone.registry)


ZCML_LAYER = ZCMLLayer()


class TabbedViewLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        import z3c.autoinclude
        xmlconfig.file('meta.zcml', z3c.autoinclude,
                       context=configurationContext)
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <includePlugins package="plone" />'
            '</configure>',
            context=configurationContext)

        import ftw.tabbedview.tests
        xmlconfig.file('tests.zcml', ftw.tabbedview.tests,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.tabbedview:default')


TABBED_VIEW_LAYER = TabbedViewLayer()
TABBEDVIEW_INTEGRATION_TESTING = IntegrationTesting(
    bases=(TABBED_VIEW_LAYER, ), name="ftw.tabbedview:integration")
TABBEDVIEW_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(TABBED_VIEW_LAYER, ), name="ftw.tabbedview:functional")
