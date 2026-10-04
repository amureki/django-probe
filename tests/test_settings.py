from __future__ import annotations

from unittest import TestCase

from django import VERSION as DJANGO_VERSION
from django.conf import global_settings

from django_probe.settings import DJANGO_SETTING_NAMES, DJANGO_SETTING_NAMES_BY_VERSION


class DjangoSettingCatalogTests(TestCase):
    def test_installed_settings(self):
        """The installed Django release matches its committed setting catalog."""
        version = ".".join(str(part) for part in DJANGO_VERSION[:2])

        self.assertIn(version, DJANGO_SETTING_NAMES_BY_VERSION)
        self.assertEqual(
            frozenset(name for name in vars(global_settings) if name.isupper()),
            DJANGO_SETTING_NAMES_BY_VERSION[version],
        )

    def test_contrib_settings(self):
        global_settings = frozenset().union(*DJANGO_SETTING_NAMES_BY_VERSION.values())

        self.assertEqual(
            DJANGO_SETTING_NAMES - global_settings,
            {
                "GDAL_LIBRARY_PATH",
                "GEOIP_CITY",
                "GEOIP_COUNTRY",
                "GEOIP_PATH",
                "GEOS_LIBRARY_PATH",
                "MESSAGE_LEVEL",
                "MESSAGE_TAGS",
                "POSTGIS_VERSION",
                "SITE_ID",
                "SPATIALITE_LIBRARY_PATH",
            },
        )
