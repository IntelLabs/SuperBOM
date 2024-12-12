# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache 2.0

# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: GPL-3.0-or-later

import requests

from superbom.utils.licenseutils import checklicense


def get_license(source):
    if "github.com" not in source:
        source = _search(source)
    return _lookuplicense(source)


def _search(repo_name):
    # TODO: Hacky way to search for a repo. Need to improve this.
    # For now, always skip if the repo_name is 'python'
    if repo_name == "python":
        return None

    url = f"https://api.github.com/search/repositories?q={repo_name}+in:name"
    response = requests.get(url)
    if response.status_code == 200:
        repos = response.json()["items"]

        for repo in repos:
            if repo["name"] == repo_name:
                return repo["html_url"]

    return None


def _lookuplicense(source_url: str):

    try:
        owner, repo = source_url.split("github.com/")[1].split("/")
    except Exception:
        return False, None

    url = f"https://api.github.com/repos/{owner}/{repo}/license"
    response = requests.get(url)
    if response.status_code == 200:
        tmp = response.json()

        if tmp.get("license"):
            license = tmp["license"]["spdx_id"]
            return checklicense(license)

    return False, None
