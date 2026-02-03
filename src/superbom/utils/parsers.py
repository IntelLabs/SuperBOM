# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache 2.0

import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Set, Union

import tomli
import yaml
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.markers import Marker


@dataclass
class Dependency:
    """A simple dependency class to replace Poetry's Factory.create_dependency"""
    name: str
    constraint: Union[str, SpecifierSet]
    extras: Optional[Set[str]] = None
    marker: Optional[Marker] = None
    
    def __post_init__(self):
        if isinstance(self.constraint, str):
            self.constraint = SpecifierSet(self.constraint) if self.constraint else SpecifierSet()
        if self.extras is None:
            self.extras = set()
    
    @classmethod
    def create_dependency(cls, name: str, constraint: Union[str, SpecifierSet] = "", 
                         extras: Optional[Set[str]] = None, marker: Optional[Marker] = None):
        """Factory method to create a dependency, similar to Poetry's Factory.create_dependency"""
        return cls(name=name, constraint=constraint, extras=extras or set(), marker=marker)


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
                    package = Dependency.create_dependency(
                        package["name"], str(package["specifier"]), package["extras"], package["marker"]
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
                    package = Dependency.create_dependency(
                        package["name"], str(package["specifier"]), package["extras"], package["marker"]
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
            pip_packages[i] = Dependency.create_dependency(
                tmp["name"], str(tmp["specifier"]), tmp["extras"], tmp["marker"]
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
                Dependency.create_dependency(
                    tmp["name"], str(tmp["specifier"]), tmp["extras"], tmp["marker"]
                )
            )

    return packages


def parse_poetry_toml(file_path):
    """Parse a pyproject.toml file, supporting both Poetry and modern PEP 621 format"""
    packages = []
    file_path = Path(file_path)
    
    with open(file_path, "rb") as f:
        data = tomli.load(f)
    
    # Try Poetry format first (legacy)
    if "tool" in data and "poetry" in data["tool"]:
        poetry_config = data["tool"]["poetry"]
        
        deps = poetry_config.get("dependencies", {})
        dev_deps = poetry_config.get("dev-dependencies", {})
        
        # Also check for group dependencies
        if "group" in poetry_config:
            for group_name, group_config in poetry_config["group"].items():
                if "dependencies" in group_config:
                    dev_deps.update(group_config["dependencies"])
        
        all_deps = {**deps, **dev_deps}
        
        for dep_name, constraint in all_deps.items():
            if dep_name == "python":  # Skip Python version constraint
                continue
            
            # Handle different constraint formats
            if isinstance(constraint, str):
                constraint_str = constraint
            elif isinstance(constraint, dict):
                # Handle complex constraints like {version = "^1.0", extras = ["dev"]}
                constraint_str = constraint.get("version", "")
            else:
                constraint_str = str(constraint)
            
            # Convert Poetry caret notation to standard format
            if constraint_str.startswith("^"):
                constraint_str = ">=" + constraint_str[1:]
            
            packages.append(Dependency.create_dependency(dep_name, constraint_str))
    
    return packages
