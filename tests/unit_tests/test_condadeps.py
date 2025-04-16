# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache 2.0

import unittest
from unittest.mock import PropertyMock, patch

from superbom.utils.packageindexes.conda.condadependencies import CondaPackageUtil


class TestCondaPackageUtil(unittest.TestCase):
    def setUp(self):
        self.util = CondaPackageUtil()

    def test_parse_conda_dependency(self):
        dependency = "conda-forge::numpy>=1.18.0"
        result = self.util.parse_conda_dependency(dependency)
        expected = {
            "channel": "conda-forge",
            "package": "numpy",
            "version": "1.18.0",
            "build": None,
        }
        self.assertEqual(result, expected)

    @patch("superbom.utils.packageindexes.conda.condadependencies.CondaCache.get_cache")
    def test_lookup_package(self, mock_get_cache):
        mock_get_cache.return_value = {
            "packages": {"numpy-1.18.0": {"name": "numpy", "version": "1.18.0"}},
            "packages.conda": {},
        }
        result = self.util.lookup_package_from_cache("conda-forge", "noarch", "numpy", "1.18.0")
        self.assertIsNotNone(result)
        self.assertEqual(result[1]["name"], "numpy")
        self.assertEqual(result[1]["version"], "1.18.0")

    @patch("superbom.utils.packageindexes.conda.condadependencies.CondaCache.get_cache")
    def test_lookup_package_not_found(self, mock_get_cache):
        mock_get_cache.return_value = {"packages": {}, "packages.conda": {}}
        result = self.util.lookup_package_from_cache("conda-forge", "noarch", "numpy", "1.18.0")
        self.assertIsNone(result)

    def test_find_license(self):
        dictionary = {"license": "MIT"}
        key, value = self.util._find_license(dictionary, "license")
        self.assertEqual(key, "license")
        self.assertEqual(value, "MIT")

    @patch("superbom.utils.packageindexes.conda.condacache.CondaCache.get_cache")
    @patch(
        "superbom.utils.packageindexes.conda.condacache.CondaCache.channels",
        new_callable=PropertyMock,
    )
    @patch(
        "superbom.utils.packageindexes.conda.condacache.CondaCache.platforms",
        new_callable=PropertyMock,
    )
    def test_retrieve_conda_package_info_success(
        self, mock_platforms, mock_channels, mock_get_cache
    ):

        mock_channels.return_value = ["conda-forge"]
        mock_platforms.return_value = ["noarch"]
        mock_get_cache.return_value = {
            "packages": {
                "test-package": {"name": "test-package", "version": "1.0.0", "license": "MIT"},
            },
            "packages.conda": {},
        }

        dep = "conda-forge::test-package=1.0.0"
        result = self.util.retrieve_conda_package_info(dep)

        expected = {
            "Package": "test-package",
            "Version": "1.0.0",
            "License": "MIT",
            "Validated": True,
            "Source": "conda-forge:noarch",
        }
        self.assertEqual(result, expected)

    @patch("superbom.utils.packageindexes.conda.condadependencies.CondaCache.get_cache")
    @patch(
        "superbom.utils.packageindexes.conda.condadependencies.CondaCache.channels",
        new_callable=PropertyMock,
    )
    @patch(
        "superbom.utils.packageindexes.conda.condadependencies.CondaCache.platforms",
        new_callable=PropertyMock,
    )
    def test_retrieve_conda_package_info_no_license(
        self, mock_platforms, mock_channels, mock_get_cache
    ):
        mock_channels.return_value = ["conda-forge"]
        mock_platforms.return_value = ["noarch"]
        mock_get_cache.return_value = {
            "packages": {"test-package": {"name": "test-package", "version": "1.0.0"}},
            "packages.conda": {},
        }

        dep = "conda-forge::test-package=1.0.0"
        result = self.util.retrieve_conda_package_info(dep)
        expected = {
            "Package": "test-package",
            "Version": "1.0.0",
            "License": "No License Information",
            "Validated": False,
            "Source": "conda-forge:noarch",
        }

        self.assertEqual(result, expected)

    @patch("superbom.utils.packageindexes.conda.condadependencies.CondaCache.get_cache")
    @patch(
        "superbom.utils.packageindexes.conda.condadependencies.CondaCache.channels",
        new_callable=PropertyMock,
    )
    @patch(
        "superbom.utils.packageindexes.conda.condadependencies.CondaCache.platforms",
        new_callable=PropertyMock,
    )
    def test_retrieve_conda_package_info_not_found(
        self, mock_platforms, mock_channels, mock_get_cache
    ):
        mock_channels.return_value = ["conda-forge"]
        mock_platforms.return_value = ["noarch"]
        mock_get_cache.return_value = None

        dep = "conda-forge::nonexistent-package"
        result = self.util.retrieve_conda_package_info(dep)
        expected = {
            "Package": "nonexistent-package",
            "Version": None,
            "License": "No License Information",
            "Validated": False,
            "Source": ":",
        }

        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
