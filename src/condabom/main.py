import argparse
import re
import sys
import yaml
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

    #Handle Conda Env File
    if args.filename:
        print (f"Processing conda env file: {args.filename}")
        channels, conda_packages, pip_packages = parse_conda_env(args.filename)
        packageutil = condadependencies.CondaPackageUtil()
        if args.platform:
            packageutil._cache.add_platform(args.platform)

        if channels:
            packageutil._cache.add_channels(channels)

        conda_data = packageutil.retrieve_conda_package_info(conda_packages)
        conda_pip_data = pipdependencies.get_pip_packages_data(pip_packages)
        output_data = conda_data + conda_pip_data

    # else:
    #     # Discover all environment and requirements files
    #             conda_packages, pip_packages = discover_files()
        

    df = pd.DataFrame(output_data)

    if args.format == 'csv':
        df.to_csv(args.output, index=False)
    elif args.format == 'json':
        df.to_json(args.output, orient='records')
    else:
        print(df)

def main(argv=None):
    # Create top-level parser
    parser = argparse.ArgumentParser(
        description='Demo program showing argparse features'
    )

    # File command
    parser.add_argument('filename', type=str, help="Path to environment.yml file")

    # Output commands
    parser.add_argument('-o', '--output', type=str, help='Path to output file', default=sys.stdout)
    parser.add_argument('-f', '--format', type=str, help='Output format (table, csv, json) Default: table', default='table')
    
    # Platform command
    parser.add_argument('-p', '--platform', type=str, help='Additional platform to check for conda packages', default=None)

    args = parser.parse_args(argv)
    generatebom(args)

if __name__ == "__main__":
    main()