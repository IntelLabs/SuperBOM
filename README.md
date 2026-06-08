# SuperBOM
![GitHub License](https://img.shields.io/github/license/IntelLabs/SuperBOM)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/IntelLabs/SuperBOM/badge)](https://scorecard.dev/viewer/?uri=github.com/IntelLabs/SuperBOM)
[![CI](https://github.com/IntelLabs/SuperBOM/actions/workflows/main.yml/badge.svg)](https://github.com/IntelLabs/SuperBOM/actions/workflows/main.yml)
![Dependabot](https://img.shields.io/badge/dependabot-enabled-brightgreen)

![Python](https://img.shields.io/badge/python-%3E%203.11-blue)

## Features
- Automatically parses Python environment files to discover dependencies.
- Currently supports:
  - Conda (environment.yml, environment.yaml)
  - PIP (requirements.txt)
  - Poetry (pyproject.toml)
  - Modern Python projects (pyproject.toml with PEP 621 format)
- Looks up license information directly from Conda caches and PyPI.
- Can process individual files or search directories for multiple dependency files.
- Outputs detailed Bill of Materials with package versions, licenses, and validation status.

## Usage
```
usage: superbom [-h] [-o OUTPUT] [-f FORMAT] [-p PLATFORM] [-v] [-V] path

Generate a Bill of Materials (BOM)

positional arguments:
  path                  Path to environment file or directory to search.
                        (if directory, will search for .yml, .yaml, .txt, .toml files)

options:
  -h, --help            show this help message and exit
  -o, --output OUTPUT   Path to output file
  -f, --format FORMAT   Output format (table, csv, excel, json) Default: table
  -p, --platform PLATFORM
                        Additional platform to check for conda packages
  -v, --verbose         Enable verbose logging
  -V, --version         Show version and exit
```

## Examples

```bash
# Process a single requirements.txt file
superbom requirements.txt

# Process a conda environment file with table output
superbom environment.yml -f table

# Process a pyproject.toml file and save as Excel
superbom pyproject.toml -f excel -o dependencies.xlsx

# Search a directory for all dependency files and output as JSON
superbom ./my-project -f json -o bom.json

# Process with verbose logging
superbom pyproject.toml -v

# Add additional conda platform for cross-platform analysis
superbom environment.yml -p win-64
```
## Setup and Build
### Prerequisites
- Python 3.11+  
- uv (Python package manager)  
- git  

### Quick Install
For quick installation as a tool via `uv`:
```bash
uv tool install git+https://github.com/IntelLabs/SuperBOM

# with a specific tag/release
uv tool install git+https://github.com/IntelLabs/SuperBOM@v0.3.0
```

Or see below for development setup.

### Project Setup
```bash
# Navigate to project directory
cd superbom

# Install uv (if not already installed)
pip install uv

# Install project dependencies
uv sync

# Or install in editable mode
uv pip install -e .
```
### Development Setup
```bash
# Install project with development dependencies
uv pip install -e ".[dev]"

# Or use uv sync to install all dependencies including dev
uv sync

# Run commands in the uv environment
uv run superbom --help

# Or activate the virtual environment
source .venv/bin/activate  # On Unix/macOS
# .venv\Scripts\activate     # On Windows
```

### Building

```bash
# Build the project
uv build

# this will create two files in dist/:
# - superbom-x.x.x-py3-none-any.whl (Wheel file)
# - superbom-x.x.x.tar.gz (Source distribution)

# Alternative: use standard Python build tools
pip install build
python -m build
```

## 🔒 Security

SuperBOM follows security best practices:
- **Signed Releases**: All releases are cryptographically signed using Sigstore
- **Continuous Fuzzing**: Automated security fuzzing for input validation
- **SLSA Provenance**: Supply chain integrity verification
- **Regular Updates**: Automated dependency updates and security patches

For security issues, see [SECURITY.md](SECURITY.md). For release verification, see [RELEASE.md](RELEASE.md).

