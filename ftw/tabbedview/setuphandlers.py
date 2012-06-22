def set_quickupload_settings(portal):
    from collective.quickupload.browser.quickupload_settings import IQuickUploadControlPanel
    settings = IQuickUploadControlPanel(portal)
    # Limit simultaneous uploads to 1 (sequential) to avoid DB conflicts
    settings.sim_upload_limit = 1


def import_various(context):
    """Import step for configuration that is not handled in xml files.
    """
    site = context.getSite()

    # profile-ftw.tabbedview:default
    if context.readDataFile('ftw.tabbedview_default.txt'):
        pass

    # profile-ftw.tabbedview:quickupload
    if context.readDataFile('ftw.tabbedview_quickupload.txt'):
        set_quickupload_settings(site)

    # profile-ftw.tabbedview:extjs
    if context.readDataFile('ftw.tabbedview_extjs.txt'):
        pass
