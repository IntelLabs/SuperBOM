# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache 2.0

import pytest

from superbom.utils.parsers import parse_git_requirement, parse_requirement


@pytest.mark.parametrize(
    "line, expected",
    [
        ("git+https://github.com/user/repo.git#egg=package_name", "package_name"),
        ("git+https://github.com/user/repo.git", "repo"),
        ("git+https://github.com/user/repo#egg=package_name", "package_name"),
        ("git+https://github.com/user/repo", "repo"),
        ("https://github.com/user/repo.git#egg=package_name", "package_name"),
        ("https://github.com/user/repo.git", "repo"),
        ("https://github.com/user/repo", "repo"),
        ("git+ssh://git@github.com:user/repo.git#egg=package_name", "package_name"),
        ("git+ssh://git@github.com:user/repo.git", "repo"),
        ("git+ssh://git@github.com:user/repo", "repo"),
        ("invalid_git_url", None),
        ("", None),
    ],
)
def test_parse_git_requirement(line, expected):
    assert parse_git_requirement(line) == expected


@pytest.mark.parametrize(
    "requirement_str, expected",
    [
        (
            "package_name>=1.0.0",
            {
                "name": "package_name",
                "specifier": ">=1.0.0",
                "extras": set(),
                "marker": None,
            },
        ),
        (
            "package_name[extra1,extra2]>=1.0.0",
            {
                "name": "package_name",
                "specifier": ">=1.0.0",
                "extras": {"extra1", "extra2"},
                "marker": None,
            },
        ),
        (
            "package_name; python_version<'3.8'",
            {
                "name": "package_name",
                "specifier": "",
                "extras": set(),
                "marker": 'python_version < "3.8"',
            },
        ),
        (
            "package_name[extra1]; python_version<'3.8'",
            {
                "name": "package_name",
                "specifier": "",
                "extras": {"extra1"},
                "marker": 'python_version < "3.8"',
            },
        ),
        (
            "",
            None,
        ),
    ],
)
def test_parse_requirement(requirement_str, expected):
    result = parse_requirement(requirement_str)
    if expected is None:
        assert result is None
    else:
        assert result["name"] == expected["name"]
        assert str(result["specifier"]) == expected["specifier"]
        assert result["extras"] == expected["extras"]

        if expected["marker"] is None:
            assert result["marker"] is None
        else:
            assert str(result["marker"]) == expected["marker"]
