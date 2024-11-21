# CondaBOM

## Features
- Automatically parses Conda environment.py file to discover
  - channels
  - packages
  - pip packages
- Looks up license information directly from Conda cache and PyPi.

## Usage
```
usage: condabom [-h] [-o OUTPUT] [-f FORMAT] [-p PLATFORM] filename

Generate a Bill of Materials (BOM) for a Conda environment file or a requirements.txt file

positional arguments:
  filename              Path to environment.yml file

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
cd condabom

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
# - condabom-x.x.x-py3-none-any.whl (Wheel file)
# - condabom-x.x.x.tar.gz (Source distribution)
```

