# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache 2.0

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Union

import pandas as pd

from superbom.utils.packageindexes.conda.condadependencies import CondaPackageUtil
from superbom.utils.packageindexes.pypi.pipdependencies import PyPIPackageUtil
from superbom.utils.logger import AppLogger
from superbom.utils.parsers import (
    parse_conda_env,
    parse_poetry_toml,
    parse_requirements,
)

logger = AppLogger().get_logger()


def filter_by_extensions(input: Union[str, Path], extensions: Union[str, List[str]]) -> List[Path]:
    """Filter directory contents by file extensions."""
    if isinstance(input, str):
        input = Path(input)

    # Normalize extensions to list of lowercase strings with dots
    if isinstance(extensions, str):
        extensions = [extensions]
    exts = [f".{ext.lower().strip('.')}" for ext in extensions]

    if Path.is_file(input):
        return [input] if input.suffix.lower() in exts else []

    # Filter files
    files = []
    for f in input.iterdir():
        if f.is_file() and f.suffix.lower() in exts:
            files.append(f)
        elif f.is_dir():
            files.extend(filter_by_extensions(f, extensions))
    return files


def save_results(results: Dict[str, pd.DataFrame], output_path: str, format: str):
    if format == "excel":
        try:
            with pd.ExcelWriter(output_path, engine="openpyxl", mode="w") as writer:
                for sheet_name, df in results.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        except Exception as e:
            logger.error(f"Error writing to Excel file: {e}")
    else:
        # Handle other formats
        for result, df in results.items():
            if format == "csv":
                df.to_csv(f"{result}-dependencies.json", index=False)
            elif format == "json":
                df.to_json(f"{result}-dependencies.csv", orient="records")
            else:
                logger.info(f"License Info: {result}\n{df}")


def generatebom(args: argparse.ArgumentParser):
    """
    Generates a Bill of Materials (BOM) from environment files.

    Args:
        args (argparse.ArgumentParser): Command-line arguments containing the following attributes:
            - path (str): Path to the directory or file containing environment files.
            - verbose (bool): Flag to enable verbose logging.
            - platform (str, optional): Platform for which to retrieve package information.
            - output (str, optional): Path to save the output file.
            - format (str, optional): Format of the output file (e.g., 'table', 'json').

    Returns:
        None: The function saves the BOM to the specified output path in the specified format.

    Environment Files:
        - .yml: Conda environment files.
        - .txt: Pip requirements files.
        - .toml: Poetry files.

    Processing Steps:
        1. Filters environment files based on extensions (yml, txt, toml).
        2. Parses each environment file and retrieves package information.
        3. Conda environment files:
            - Parses channels, conda packages, and pip packages.
            - Retrieves package information from Conda and Pip.
        4. Pip requirements files:
            - Parses pip packages.
            - Retrieves package information from Pip.
        5. Poetry files:
            - Parses pip packages.
            - Retrieves package information from Pip.
        6. Compiles the package information into a DataFrame.
        7. Saves the results to the specified output path in the specified format.
    """
    results: {str, pd.DataFrame} = {}

    if args.verbose:
        logger.setLevel("DEBUG")

    env_files = filter_by_extensions(args.path, ["yml", "txt", "toml"])

    packageutil = CondaPackageUtil()
    pipdependencies = PyPIPackageUtil()

    for env_file in env_files:
        output_data = []

        if env_file.suffix.lower() == ".yml":
            logger.info(f"Processing conda env file: {env_file}")
            channels, conda_packages, pip_packages = parse_conda_env(env_file)
            if args.platform:
                packageutil._cache.add_platform(args.platform)

            if channels:
                packageutil._cache.add_channels(channels)
            else:
                logger.warning("No channels specified in environment file. Using defaults.")
                packageutil._cache.add_channels(packageutil._cache.DEFAULT_CHANNELS)

            conda_data = packageutil.retrieve_conda_package_info(conda_packages)
            conda_pip_data = pipdependencies.get_pip_packages_data(pip_packages)
            output_data.extend(conda_data + conda_pip_data)
            output_data = conda_data + conda_pip_data

        elif env_file.suffix.lower() == ".txt":
            logger.info(f"Processing pip requirements file: {env_file}")
            pip_packages = parse_requirements(env_file)
            pip_data = pipdependencies.get_pip_packages_data(pip_packages)
            output_data.extend(pip_data)

        elif env_file.suffix.lower() == ".toml":
            logger.info(f"Processing poetry file: {env_file}")

            pip_packages = parse_poetry_toml(env_file)
            pip_data = pipdependencies.get_pip_packages_data(pip_packages)
            output_data.extend(pip_data)

        df = pd.DataFrame(output_data)
        results[env_file.name] = df

    # Save results
    # output_path = args.output if args.output else 'bom.xlsx'
    # format = args.format if args.format else 'table'
    save_results(results, args.output, args.format)


class RequiredOutputFormat(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values not in ["table", "csv", "excel", "json"]:
            raise ValueError("Output format must be one of: table, csv, excel, json")

        if values == "excel" and not namespace.output:
            raise ValueError("Output (-o/--output) must be specified when format is 'Excel'")
        setattr(namespace, self.dest, values)


def main(argv=None):

    # Create top-level parser
    parser = argparse.ArgumentParser(description="Generate a Bill of Materials (BOM)")

    # File command
    parser.add_argument(
        "path",
        type=str,
        help="Path to environment file or directory to search.  (if directory, will search for .yml, .txt, .toml files)",
    )

    # Output commands
    parser.add_argument("-o", "--output", type=str, default=sys.stdout, help="Path to output file")

    parser.add_argument(
        "-f",
        "--format",
        default="table",
        type=str,
        action=RequiredOutputFormat,
        help="Output format (table, csv, excel, json) Default: table",
    )

    # Platform command
    parser.add_argument(
        "-p",
        "--platform",
        type=str,
        help="Additional platform to check for conda packages",
        default=None,
    )

    # Verbosity command
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args(argv)
    generatebom(args)


if __name__ == "__main__": # pragma: no cover
    main()
