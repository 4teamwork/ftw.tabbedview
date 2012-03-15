from collective.quickupload.browser.quick_upload import QuickUploadInit, FLASH_UPLOAD_JS, XHR_UPLOAD_JS


class FtwUploadInit(QuickUploadInit):

    def __call__(self, for_id="uploader"):
        self.uploader_id = for_id
        settings = self.upload_settings()
        if self.qup_prefs.use_flashupload :
            return FLASH_UPLOAD_JS % settings
        return XHR_UPLOAD_JS % settings

