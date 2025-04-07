# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache 2.0

import re
from pathlib import Path

import tomli
import yaml
from packaging.requirements import Requirement
from poetry.core.factory import Factory
from poetry.core.pyproject.toml import PyProjectTOML


def parse_git_requirement(line):
    """Extracts package name from a git+ requirement line."""

    # Check if the package name is explicitly defined with #egg=
    egg_match = re.search(r"#egg=([\w-]+)", line)
    if egg_match:
        return egg_match.group(1)

    # If no #egg=, try to extract from the repository URL
    repo_match = re.search(r"[:\/][^\/]+\/([^\/#]+?)(?:\.git)?(?:[#?].*)?$", line)
    if repo_match:
        return repo_match.group(1)  # Returns the repo name as a fallback

    return None  # If it can't find a valid name


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


def parse_requirements(file_path):  # pragma: no cover
    with open(file_path, "r") as file:
        packages = []
        for line in file.readlines():
            # Skip comments and empty lines
            if line.startswith("#") or line.startswith("-e") or not line.strip():
                continue

            if line.startswith("git+"):
                # Handle git URLs
                line = line.split("git+")[-1].strip()
                package = parse_git_requirement(line)
                package = parse_requirement(package)
                if package is not None:
                    package = Factory.create_dependency(
                        package["name"], package["specifier"], package["extras"], package["marker"]
                    )
                    packages.append(package)
                continue

            # Check if it's a reference to another file with a `-r` prefix
            if line.startswith("-r"):
                # Extract the file path
                ref_file_path = line.split()[1].strip()

                # Check if the file path is relative or absolute
                if not Path(ref_file_path).is_absolute():
                    ref_file_path = Path(file_path).parent / ref_file_path
                # Check if the file exists
                if not Path(ref_file_path).exists():
                    print(f"Referenced file does not exist: {ref_file_path}")
                    continue

                # Recursively parse the referenced file
                packages.extend(parse_requirements(ref_file_path))

            else:
                package = parse_requirement(line.strip("\n"))

                if package is not None:
                    package = Factory.create_dependency(
                        package["name"], package["specifier"], package["extras"], package["marker"]
                    )
                    packages.append(package)

    return packages


def parse_conda_env(file_path):
    with open(file_path, "r") as file:
        data = None

        try:
            data = yaml.safe_load(file)
        except Exception as e:
            print(f"Error parsing YAML file: {file_path}")
            return [], [], []

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


def extract_toml_dependencies(file_path):  # pragma: no cover
    packages = []

    with open(file_path, "rb") as f:
        data = tomli.load(f)

    dependencies = set()

    # Extract main dependencies (if present)
    if "dependencies" in data.get("project", {}):
        dependencies.update(data["project"]["dependencies"])

    # Extract optional dependencies
    for extra in data.get("project", {}).get("optional-dependencies", {}).values():
        dependencies.update(extra)

    # create dependencies from the main dependencies
    for dep in dependencies:
        if isinstance(dep, str):
            tmp = parse_requirement(dep.strip())

            if tmp is None:
                continue

            packages.append(
                Factory.create_dependency(
                    tmp["name"], tmp["specifier"], tmp["extras"], tmp["marker"]
                )
            )

    return packages


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
