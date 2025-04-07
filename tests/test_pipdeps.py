# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache 2.0

import unittest
from unittest.mock import MagicMock, patch

from superbom.utils.packageindexes.pypi.pipdependencies import PyPIPackageUtil


class TestPyPIPackageUtil(unittest.TestCase):
    @patch("superbom.utils.packageindexes.pypi.pipdependencies.requests.get")
    @patch("superbom.utils.packageindexes.pypi.pipdependencies.pypiutils.get_license")
    def test_get_pip_packages_data_pypi(self, mock_get_license, mock_requests_get):
        mock_package = MagicMock()
        mock_package.name = "testpackage"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "info": {"name": "testpackage", "version": "1.0.0", "license": "MIT"}
        }
        mock_requests_get.return_value = mock_response
        mock_get_license.return_value = (True, "MIT")

        util = PyPIPackageUtil()
        result = util.get_pip_packages_data([mock_package])

        expected_result = [
            {
                "Package": "testpackage",
                "Version": "1.0.0",
                "License": "MIT",
                "Validated": True,
                "Source": "pypi",
            }
        ]
        self.assertEqual(result, expected_result)

    @patch("superbom.utils.packageindexes.pypi.pipdependencies.requests.get")
    @patch("superbom.utils.packageindexes.pypi.pipdependencies.githubutils.get_license")
    def test_get_pip_packages_data_github(self, mock_get_license, mock_requests_get):
        mock_package = MagicMock()
        mock_package.name = "testpackage"

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_requests_get.return_value = mock_response
        mock_get_license.return_value = (True, "MIT")

        util = PyPIPackageUtil()
        result = util.get_pip_packages_data([mock_package])

        expected_result = [
            {
                "Package": "testpackage",
                "Version": "N/A",
                "License": "MIT",
                "Validated": True,
                "Source": "github",
            }
        ]
        self.assertEqual(result, expected_result)

    @patch("superbom.utils.packageindexes.pypi.pipdependencies.requests.get")
    def test_get_pip_packages_data_python(self, mock_requests_get):
        mock_package = MagicMock()
        mock_package.name = "python"

        util = PyPIPackageUtil()
        result = util.get_pip_packages_data([mock_package])

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
