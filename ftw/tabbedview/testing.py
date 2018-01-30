from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.testing.layer import ComponentRegistryLayer
from pkg_resources import get_distribution
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from z3c.autoinclude.api import disable_dependencies
from z3c.autoinclude.api import disable_plugins
from zope.configuration import xmlconfig


IS_PLONE_5 = get_distribution('Plone').version >= '5'


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

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

        import ftw.tabbedview.tests
        xmlconfig.file('tests.zcml', ftw.tabbedview.tests,
                       context=configurationContext)
        xmlconfig.file('tabs.zcml', ftw.tabbedview.tests,
                       context=configurationContext)
        xmlconfig.file('profiles/profiles.zcml', ftw.tabbedview.tests,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.tabbedview:default')
        applyProfile(portal, 'ftw.tabbedview.tests:tabs')
        if IS_PLONE_5:
            applyProfile(portal, 'plone.app.contenttypes:default')


TABBED_VIEW_LAYER = TabbedViewLayer()
TABBEDVIEW_INTEGRATION_TESTING = IntegrationTesting(
    bases=(TABBED_VIEW_LAYER, ), name="ftw.tabbedview:integration")
TABBEDVIEW_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(TABBED_VIEW_LAYER, set_builder_session_factory(functional_session_factory)),
    name="ftw.tabbedview:functional")
