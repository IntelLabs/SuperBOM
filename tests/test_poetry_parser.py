# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache 2.0

import unittest
from pathlib import Path

from poetry.core.packages.dependency import Dependency

from superbom.utils.parsers import parse_poetry_toml


class TestParsePoetryToml(unittest.TestCase):
    def setUp(self):
        self.valid_toml_content = """
        [tool.poetry]
        name = "example"
        version = "0.1.0"
        description = ""
        authors = ["Author <author@example.com>"]

        [tool.poetry.dependencies]
        python = "^3.8"
        requests = "^2.25.1"

        [tool.poetry.dev-dependencies]
        pytest = "^6.2.2"
        """

        self.invalid_toml_content = """
        [tool.poetry]
        name = "example"
        version = "0.1.0"
        description = ""
        authors = ["Author <author@example.com>"]

        [tool.poetry.dependencies]
        python = "^3.8"
        requests = "^2.25.1"

        [tool.poetry.dev-dependencies]
        pytest = "^6.2.2"
        """

        self.valid_toml_path = Path("valid_pyproject.toml")
        self.invalid_toml_path = Path("invalid_pyproject.toml")

        with open(self.valid_toml_path, "w") as file:
            file.write(self.valid_toml_content)

        with open(self.invalid_toml_path, "w") as file:
            file.write(self.invalid_toml_content)

    def tearDown(self):
        self.valid_toml_path.unlink()
        self.invalid_toml_path.unlink()

    def test_parse_poetry_toml_valid(self):
        packages = parse_poetry_toml(self.valid_toml_path)
        self.assertEqual(len(packages), 3)
        self.assertIsInstance(packages[0], Dependency)
        self.assertEqual(packages[0].name, "python")
        self.assertEqual(packages[1].name, "requests")
        self.assertEqual(packages[2].name, "pytest")

    def test_parse_poetry_toml_invalid(self):
        packages = parse_poetry_toml(self.invalid_toml_path)
        self.assertEqual(len(packages), 3)
        self.assertIsInstance(packages[0], Dependency)
        self.assertEqual(packages[0].name, "python")
        self.assertEqual(packages[1].name, "requests")
        self.assertEqual(packages[2].name, "pytest")


if __name__ == "__main__":
    unittest.main()
