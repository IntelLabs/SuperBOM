#!/usr/bin/env python3
"""
Fuzzing target for SuperBOM parsers using a simple random fuzzing approach.
This provides cross-platform fuzzing without requiring libFuzzer.
"""

import sys
import tempfile
import random
import string
from pathlib import Path

# Add the src directory to the path so we can import superbom
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from superbom.utils.parsers import (
    parse_requirements, 
    parse_conda_env, 
    parse_poetry_toml,
    extract_toml_dependencies,
    parse_requirement,
    parse_git_requirement
)


def generate_random_string(length_range=(0, 1000)):
    """Generate a random string for fuzzing"""
    length = random.randint(*length_range)
    chars = string.ascii_letters + string.digits + string.punctuation + " \n\t"
    return ''.join(random.choice(chars) for _ in range(length))


def generate_malformed_requirements():
    """Generate malformed requirements.txt content"""
    lines = []
    for _ in range(random.randint(0, 50)):
        # Mix valid-looking and random content
        if random.random() < 0.3:
            # Sometimes generate valid-looking lines
            pkg = random.choice(["requests", "numpy", "pandas", "flask"])
            op = random.choice(["==", ">=", "<=", "~=", ">", "<"])
            ver = f"{random.randint(0,9)}.{random.randint(0,20)}.{random.randint(0,50)}"
            lines.append(f"{pkg}{op}{ver}")
        else:
            # Generate random content
            lines.append(generate_random_string((0, 100)))
    return "\n".join(lines)


def generate_malformed_yaml():
    """Generate malformed YAML content"""
    templates = [
        "name: {}\ndependencies:\n  - {}\n  - pip:\n    - {}",
        "dependencies:\n{}\nchannels:\n  - {}",
        "{}: {}\n{}",
        "name: test\n" + generate_random_string((0, 500)),
    ]
    template = random.choice(templates)
    return template.format(*[generate_random_string((0, 50)) for _ in range(10)][:template.count("{}")])


def generate_malformed_toml():
    """Generate malformed TOML content"""
    templates = [
        "[tool.poetry]\nname = '{}'\n[tool.poetry.dependencies]\n{} = '{}'",
        "[project]\nname = '{}'\ndependencies = ['{}']\n{}",
        "{} = {}\n[{}]\n{}",
        generate_random_string((0, 200)),
    ]
    template = random.choice(templates)
    return template.format(*[generate_random_string((0, 30)) for _ in range(10)][:template.count("{}")])


def fuzz_parse_requirements(iterations=100):
    """Fuzz the parse_requirements function"""
    crashes = 0
    for i in range(iterations):
        try:
            content = generate_malformed_requirements()
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(content)
                f.flush()
                parse_requirements(f.name)
                Path(f.name).unlink()
        except Exception as e:
            # Log interesting crashes
            if "RecursionError" in str(type(e)) or "MemoryError" in str(type(e)):
                print(f"⚠️  Potential issue in parse_requirements: {type(e).__name__}")
                crashes += 1
    return crashes


def fuzz_parse_conda_env(iterations=100):
    """Fuzz the parse_conda_env function"""
    crashes = 0
    for i in range(iterations):
        try:
            content = generate_malformed_yaml()
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
                f.write(content)
                f.flush()
                parse_conda_env(f.name)
                Path(f.name).unlink()
        except Exception as e:
            if "RecursionError" in str(type(e)) or "MemoryError" in str(type(e)):
                print(f"⚠️  Potential issue in parse_conda_env: {type(e).__name__}")
                crashes += 1
    return crashes


def fuzz_parse_toml(iterations=100):
    """Fuzz TOML parsing functions"""
    crashes = 0
    for i in range(iterations):
        try:
            content = generate_malformed_toml()
            with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
                f.write(content)
                f.flush()
                parse_poetry_toml(f.name)
                extract_toml_dependencies(f.name)
                Path(f.name).unlink()
        except Exception as e:
            if "RecursionError" in str(type(e)) or "MemoryError" in str(type(e)):
                print(f"⚠️  Potential issue in TOML parsing: {type(e).__name__}")
                crashes += 1
    return crashes


def fuzz_parse_requirement_string(iterations=500):
    """Fuzz requirement string parsing"""
    crashes = 0
    for i in range(iterations):
        try:
            requirement_str = generate_random_string((0, 200))
            parse_requirement(requirement_str)
            parse_git_requirement(requirement_str)
        except Exception as e:
            if "RecursionError" in str(type(e)) or "MemoryError" in str(type(e)):
                print(f"⚠️  Potential issue in requirement parsing: {type(e).__name__}")
                crashes += 1
    return crashes


def main():
    """Main fuzzing entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python fuzz_parsers.py [iterations_per_function]")
        print("Default: 100 iterations per function")
        return
    
    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    
    print(f"🔍 Starting fuzzing with {iterations} iterations per function...")
    
    total_crashes = 0
    
    print("📝 Fuzzing requirements.txt parsing...")
    total_crashes += fuzz_parse_requirements(iterations)
    
    print("📦 Fuzzing conda environment parsing...")
    total_crashes += fuzz_parse_conda_env(iterations)
    
    print("⚙️  Fuzzing TOML parsing...")
    total_crashes += fuzz_parse_toml(iterations)
    
    print("🔗 Fuzzing requirement string parsing...")
    total_crashes += fuzz_parse_requirement_string(iterations * 5)  # More iterations for faster function
    
    print(f"\n✅ Fuzzing completed!")
    print(f"🐛 Total potential issues found: {total_crashes}")
    
    if total_crashes > 0:
        print("⚠️  Some potential issues were detected. Review the output above.")
        return 1
    else:
        print("🎉 No major issues detected!")
        return 0


if __name__ == "__main__":
    sys.exit(main())