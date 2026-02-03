# Fuzzing for SuperBOM

This directory contains fuzzing tests for the SuperBOM project to help discover parsing vulnerabilities and edge cases.

## Fuzzing Approaches

### 1. Atheris Fuzzing (`fuzz_parsers.py`)
Uses Google's Atheris engine for coverage-guided fuzzing of parser functions:
- Tests all major parsing functions with malformed input
- Generates random byte sequences and converts them to strings
- Focuses on file format parsers (requirements.txt, YAML, TOML)

### 2. Property-Based Testing (`fuzz_hypothesis.py`)
Uses Hypothesis for structured property-based testing:
- Generates semi-valid input structures
- Tests parsing functions with edge cases
- Validates that parsers handle malformed but structured input gracefully

## Running Fuzzing Locally

### Prerequisites
```bash
# Install fuzzing dependencies
uv add --group dev atheris hypothesis tomli-w
```

### Run Atheris Fuzzing
```bash
# Run for 60 seconds
python fuzz/fuzz_parsers.py -max_total_time=60

# Run with specific number of iterations
python fuzz/fuzz_parsers.py -runs=10000
```

### Run Property-Based Testing
```bash
# Run hypothesis-based fuzzing
python -m pytest fuzz/fuzz_hypothesis.py -v
```

## CI Integration

The fuzzing tests are integrated into the GitHub Actions workflow:
- Atheris fuzzing runs for 300 seconds on each PR and push
- Property-based tests run as part of the regular test suite
- Results are uploaded as artifacts for analysis

## OSSF Scorecard Compliance

This fuzzing setup satisfies OSSF Scorecard requirements by:
- ✅ Having continuous fuzzing in CI
- ✅ Using industry-standard fuzzing tools (Atheris)
- ✅ Covering critical parsing code paths
- ✅ Running automatically on all changes
- ✅ Providing structured and unstructured fuzzing approaches