# SuperBOM

## Features
- Automatically parses python env files to discover dependencies.
- Currently supports:
  - Conda (environment.yml)
  - PIP (requirements.txt)
  - Poetry (pyproject.toml)
- Looks up license information directly from Conda caches and PyPi.

## Usage
```
usage: superbom [-h] [-o OUTPUT] [-f FORMAT] [-p PLATFORM] filename

positional arguments:
  filename              Path to input file

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Path to output file
  -f FORMAT, --format FORMAT
                        Output format (table, csv, json) Default: table
  -p PLATFORM, --platform PLATFORM
                        Additional platform to check for conda packages
```
## Setup and Build
### Prerequisites
- Python 3.12+  
- poetry (Python package manager)  
- git  

### Project Setup
```
# Navigate to project directory
cd superbom

# Initialize poetry environment with Python 3.12+
poetry env use python3.12

# Install project dependencies
poetry install
```
### Development Setup
```
# Activate the poetry shell
poetry shell

# Install dependencies
poetry install
```

### Building

```
# Build the project
poetry build

# this will create two files in dist/:
# - superbom-x.x.x-py3-none-any.whl (Wheel file)
# - superbom-x.x.x.tar.gz (Source distribution)
```

