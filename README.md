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
