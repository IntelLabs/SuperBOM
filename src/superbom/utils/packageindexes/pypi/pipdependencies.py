# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache 2.0

import requests

import superbom.utils.packageindexes.pypi.pypiutils as pypiutils
from superbom.utils import githubutils
from superbom.utils.logger import AppLogger


class PyPIPackageUtil:
    def __init__(self):
        self.logger = AppLogger().get_logger()

    def _getpypimetadata(self, package):
        package_data = None

        # Download package metadata from pypi
        url = f"https://pypi.org/pypi/{package.name}/json"

        response = requests.get(url)
        if response.status_code == 200:
            tmp = response.json()
            package_data = tmp["info"]

        return package_data

    def get_pip_package_data(self, package) -> dict:
        package_data = {}

        # Skip python package
        if package.name == "python":
            return package_data

        metadata = self._getpypimetadata(package)

        if metadata:
            name = metadata.get("name", "N/A")
            version = metadata.get("version", "N/A")
            validated, license = pypiutils.get_license(metadata)
            source = "pypi"

            package_data = {
                "Package": name,
                "Version": version,
                "License": license,
                "Validated": validated,
                "Source": source,
            }
            self.logger.debug(
                f"Package: {name}, Version: {version}, License: {license}, Source: {source}"
            )
        # HACK: Fix this
        else:
            # try to get license from github
            self.logger.warning(f"Package: {package.name} not found on PyPI")
            validated, license = githubutils.get_license(package.name)
            version = "N/A"
            source = "github"
            package_data = {
                "Package": package.name,
                "Version": version,
                "License": license,
                "Validated": validated,
                "Source": source,
            }

        return package_data
