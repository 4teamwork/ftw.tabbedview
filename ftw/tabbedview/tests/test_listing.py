from ftw.tabbedview.testing import IS_PLONE_5
from ftw.tabbedview.testing import TABBEDVIEW_FUNCTIONAL_TESTING
from Products.CMFPlone.utils import getToolByName
from unittest import TestCase


class TestListingView(TestCase):
    """This test case by no means covers all of ListingView.

    It was simply written as a regression test when fixing a bug for
    empty action lists.
    """

    layer = TABBEDVIEW_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.ai_tool = getToolByName(self.portal, 'portal_actions')

    def get_tab(self):
        tabbed_view = self.portal.restrictedTraverse('tabbed_view')
        tab = tabbed_view._resolve_tab('samplecataloglisting')
        return tab

    def deactivate_all_folder_buttons_actions(self):
        if IS_PLONE_5:
            return

        category = self.ai_tool['folder_buttons']
        for action in category.objectValues():
            action.visible = False

    def test_major_actions_doesnt_fail_for_empty_list(self):
        tab = self.get_tab()
        self.deactivate_all_folder_buttons_actions()
        major_actions = tab.major_actions()

        self.assertItemsEqual([], major_actions)

    def test_minor_actions_doesnt_fail_for_empty_list(self):
        tab = self.get_tab()
        self.deactivate_all_folder_buttons_actions()
        minor_actions = tab.minor_actions()

        self.assertEqual([], minor_actions)

    def test_major_buttons_doesnt_fail_for_empty_list(self):
        tab = self.get_tab()
        self.deactivate_all_folder_buttons_actions()
        major_buttons = tab.major_buttons()

        self.assertEqual([], major_buttons)

    def test_minor_buttons_doesnt_fail_for_empty_list(self):
        tab = self.get_tab()
        self.deactivate_all_folder_buttons_actions()
        minor_buttons = tab.minor_buttons()

        self.assertEqual([], minor_buttons)
