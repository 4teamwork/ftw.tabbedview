from ftw.testing.layer import ComponentRegistryLayer
from z3c.autoinclude.api import disable_dependencies
from z3c.autoinclude.api import disable_plugins


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
