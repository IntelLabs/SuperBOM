# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache 2.0


import requests

import superbom.utils.pypiutils as pypiutils
from superbom.utils import githubutils
from superbom.utils.logger import AppLogger

logger = AppLogger().get_logger()


def _getpypimetadata(package):
    package_data = None

    # Download package metadata from pypi
    url = f"https://pypi.org/pypi/{package.name}"
    # if package.specs:
    #     url += f"/{package.specs[0][1]}"
    url += "/json"

    response = requests.get(url)
    if response.status_code == 200:
        tmp = response.json()
        package_data = tmp["info"]

    return package_data


def get_pip_packages_data(packages) -> list:
    package_data = []

    for package in packages:
        # Skip python package
        if package.name == "python":
            continue

        metadata = _getpypimetadata(package)

        if metadata:
            name = metadata.get("name", "N/A")
            version = metadata.get("version", "N/A")
            validated, license = pypiutils.get_license(metadata)
            source = "pypi"

            package_data.append(
                {
                    "Package": name,
                    "Version": version,
                    "License": license,
                    "Validated": validated,
                    "Source": source,
                }
            )
            logger.info(
                f"Package: {name}, Version: {version}, License: {license}, Source: {source}"
            )
        # HACK: Fix this
        else:
            # try to get license from github
            logger.warning(f"Package: {package.name} not found on PyPI")
            validated, license = githubutils.get_license(package.name)
            version = "N/A"
            source = "github"
            package_data.append(
                {
                    "Package": package.name,
                    "Version": version,
                    "License": license,
                    "Validated": validated,
                    "Source": source,
                }
            )
            logger.info(
                f"Package: {package.name}, Version: {version}, License: {license}, Source: {source}"
            )

    return package_data
