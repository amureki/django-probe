from __future__ import annotations

from unittest import TestCase

from django import VERSION as DJANGO_VERSION
from django.conf import global_settings

from django_probe.settings import DJANGO_SETTING_NAMES_BY_VERSION


class DjangoSettingCatalogTests(TestCase):
    def test_installed_settings(self):
        """The installed Django release matches its committed setting catalog."""
        version = ".".join(str(part) for part in DJANGO_VERSION[:2])

        self.assertIn(version, DJANGO_SETTING_NAMES_BY_VERSION)
        names = DJANGO_SETTING_NAMES_BY_VERSION[version]
        self.assertLessEqual(
            frozenset(name for name in vars(global_settings) if name.isupper()), names
        )
        self.assertIn("SITE_ID", names)
        self.assertNotIn("SETTINGS_MODULE", names)

    def test_site_id(self):
        self.assertTrue(
            all(
                "SITE_ID" in names for names in DJANGO_SETTING_NAMES_BY_VERSION.values()
            )
        )
