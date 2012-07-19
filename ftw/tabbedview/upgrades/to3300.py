from ftw.upgrade import UpgradeStep


class RegisterCSS(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-ftw.tabbedview.upgrades:3300')
