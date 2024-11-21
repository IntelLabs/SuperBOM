import argparse
import re
import sys
import yaml
import os
import pandas as pd
import condabom.condadependencies as condadependencies
import condabom.pipdependencies as pipdependencies

PIP_REGEX = r'(==|>=|<=|!=|~=|===)'


def parse_requirements(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    packages = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
    return packages

def parse_conda_env(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

        conda_channels = data.get('channels', [])

        conda_packages = data.get('dependencies', [])
        pip_packages = []

        for package in conda_packages:
            if isinstance(package, dict) and 'pip' in package:
                pip_packages = package['pip']
                # Remove the pip key from the dictionary
                conda_packages.remove(package)
                break

    return conda_channels, conda_packages, pip_packages


def generatebom(args: argparse.ArgumentParser):
    output_data = []

    # # Handle PIP Requirements.txt file
    # if args.req:
    #     dep_info = self.parse_requirements(args.req)

    #     output_data = pip_deps.get_pip_packages_data(dep_info)

    if args.path:
        if os.path.isdir(args.path):
            env_files = [os.path.join(args.path, f) for f in os.listdir(args.path) if f.endswith('.yml')]
        else:
            env_files = [args.path]

        for env_file in env_files:
            print(f"Processing conda env file: {env_file}")
            channels, conda_packages, pip_packages = parse_conda_env(env_file)
            packageutil = condadependencies.CondaPackageUtil()
            if args.platform:
                packageutil._cache.add_platform(args.platform)

            if channels:
                packageutil._cache.add_channels(channels)

            conda_data = packageutil.retrieve_conda_package_info(conda_packages)
            conda_pip_data = pipdependencies.get_pip_packages_data(pip_packages)
            output_data.extend(conda_data + conda_pip_data)
        output_data = conda_data + conda_pip_data

    # else:
    #     # Discover all environment and requirements files
    #             conda_packages, pip_packages = discover_files()
        

    df = pd.DataFrame(output_data)

    if args.format == 'csv':
        df.to_csv(args.output, index=False)
    elif args.format == 'json':
        df.to_json(args.output, orient='records')
    elif args.format == 'excel':
        df.to_excel(args.output, sheet_name='Conda Dependencies', index=False)
    else:
        print(df)

def main(argv=None):
    # Create top-level parser
    parser = argparse.ArgumentParser(
        description='Generate a Bill of Materials (BOM) for a Conda environment file or a requirements.txt file'
    )

    # File command
    parser.add_argument('path', type=str, help="Path to environment.yml file or directory containing environment files")

    # Output commands
    parser.add_argument('-o', '--output', type=str, help='Path to output file', default=sys.stdout)
    parser.add_argument('-f', '--format', type=str, help='Output format (table, csv, excel, json) Default: table', default='table')
    
    # Platform command
    parser.add_argument('-p', '--platform', type=str, help='Additional platform to check for conda packages', default=None)

    args = parser.parse_args(argv)
    generatebom(args)

if __name__ == "__main__":
    main()