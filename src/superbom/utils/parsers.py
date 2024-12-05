import json
import yaml
import tomllib
from dataclasses import dataclass
from typing import Optional, Dict, Any
from typing import Dict, Any, Iterator, Union

def is_dict_like(obj: Any) -> bool:
    """Check if object is a dictionary-like structure."""
    return isinstance(obj, (dict, Dict))

def recursive_dict_iterator(data: Union[Dict[str, Any], Any]) -> Iterator[tuple[str, Any]]:
    """Recursively iterate through nested dictionaries."""
    if not is_dict_like(data):
        return

    for key, value in data.items():
        # Yield current key-value pair
        yield key, value
        
        # Recurse if value is a dictionary
        if is_dict_like(value):
            yield from recursive_dict_iterator(value)
        # Handle lists/tuples of dictionaries
        elif isinstance(value, (list, tuple)):
            for item in value:
                if is_dict_like(item):
                    yield from recursive_dict_iterator(item)

def parse_requirements(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    packages = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
    return packages

def parse_conda_env(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

        if data is None:
            return [], [], []
        
        conda_channels = data.get('channels', []) if 'channels' in data else []

        conda_packages = data.get('dependencies', []) if 'dependencies' in data else []
        pip_packages = []

        for package in conda_packages:
            if isinstance(package, dict) and 'pip' in package:
                pip_packages = package['pip']
                # Remove the pip key from the dictionary
                conda_packages.remove(package)
                break

    return conda_channels, conda_packages, pip_packages

@dataclass
class DependencySpec:
    name: str
    version: str
    optional: bool = False
    markers: Optional[str] = None
    
    @classmethod
    def from_toml(cls, name: str, spec: Any) -> "DependencySpec":
        if isinstance(spec, dict):
            spec = spec.get("version", "")

        if spec.startswith('^'):
            return f"{name}{spec.replace('^','>=')}"
        elif spec.startswith('~'):
            return f"{name}{spec.replace('~','==')}"
        elif spec[0].isdigit():
            return f"{name}=={spec}"
        else:
            return f"{name}"

# Example usage for your case:
def recursive_extract_dependencies(data: Dict[str, Any], deps: Dict[str, DependencySpec]) -> None:
    for key, value in recursive_dict_iterator(data):
        if key == "dependencies":
            for name, spec in value.items():
                deps[name] = DependencySpec.from_toml(name, spec)


def parse_poetry_toml(file_path):
    """Parse TOML content and extract dependency specifications."""
    try:
        with open(file_path, 'rb') as file:
            data = tomllib.load(file)

        deps = {}
        recursive_extract_dependencies(data, deps)

        return deps.keys()
    
    except Exception as e:
        raise ValueError(f"Failed to parse TOML: {e}")



def main():
    print("This is the main function in the parsers module. It is not intended to be run directly.")
    json.dumps(parse_poetry_toml('tests/pyproject.toml'))

if __name__ == '__main__':
    main()