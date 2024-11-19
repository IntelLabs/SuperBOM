# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache 2.0

from pathlib import Path

import yaml
from packaging.requirements import Requirement
from poetry.core.factory import Factory
from poetry.core.pyproject.toml import PyProjectTOML


def parse_requirement(requirement_str):
    try:
        requirement = Requirement(requirement_str)
        return {
            "name": requirement.name,
            "specifier": requirement.specifier,
            "extras": requirement.extras,
            "marker": requirement.marker,
        }
    except Exception as e:
        print(f"Error parsing requirement: {requirement_str}")
        print(f"Exception: {e}")
        return None


def parse_requirements(file_path):
    with open(file_path, "r") as file:
        packages = []
        for line in file.readlines():
            package = parse_requirement(line.strip("\n"))
            if package:
                package = Factory.create_dependency(
                    package["name"], package["specifier"], package["extras"], package["marker"]
                )
                packages.append(package)

    return packages


def parse_conda_env(file_path):
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)

        if data is None:
            return [], [], []

        conda_channels = data.get("channels", []) if "channels" in data else []

        conda_packages = data.get("dependencies", []) if "dependencies" in data else []
        pip_packages = []

        for package in conda_packages:
            if isinstance(package, dict) and "pip" in package:
                pip_packages = package["pip"]
                # Remove the pip key from the dictionary
                conda_packages.remove(package)
                break

    for i, package in enumerate(pip_packages):
        if isinstance(package, str):
            tmp = parse_requirement(package.strip())
            pip_packages[i] = Factory.create_dependency(
                tmp["name"], tmp["specifier"], tmp["extras"], tmp["marker"]
            )
    return conda_channels, conda_packages, pip_packages


def parse_poetry_toml(file_path):
    packages = []
    file_path = Path(file_path)
    project = PyProjectTOML(file_path)

    if project.is_poetry_project():
        deps = (
            project.poetry_config["dependencies"]
            if "dependencies" in project.poetry_config
            else {}
        )

        dev_deps = (
            project.poetry_config["dev-dependencies"]
            if "dev-dependencies" in project.poetry_config
            else {}
        )
        deps.update(dev_deps)

        for dep, constraint in deps.items():
            tmp = Factory.create_dependency(dep, constraint)
            packages.append(tmp)

    return packages
