# Security Policy
Intel is committed to rapidly addressing security vulnerabilities affecting our customers and providing clear guidance on the solution, impact, severity and mitigation. 

## Reporting a Vulnerability
Please report any security vulnerabilities in this project utilizing the guidelines [here](https://www.intel.com/content/www/us/en/security-center/vulnerability-handling-guidelines.html).

## Security Testing

### Automated Fuzzing
This project implements comprehensive fuzzing to proactively discover security vulnerabilities:

- **Continuous Fuzzing**: Automated fuzzing runs on every PR and daily via GitHub Actions
- **Coverage-Guided**: Uses Atheris for intelligent input generation and code coverage
- **Property-Based Testing**: Hypothesis-based testing validates parser behavior with edge cases
- **Parser Focus**: Targets critical parsing functions that handle untrusted input

### Running Fuzzing Locally
```bash
# Install fuzzing dependencies
uv sync --extra fuzzing

# Run interactive fuzzing
./run_fuzzing.sh

# Run specific fuzzing approaches
./run_fuzzing.sh atheris 300    # Run Atheris for 5 minutes
./run_fuzzing.sh hypothesis     # Run property-based tests
./run_fuzzing.sh both           # Run both approaches
```

### Security Measures
- Input validation for all supported file formats (requirements.txt, YAML, TOML)
- Graceful error handling for malformed input files
- Bounded resource usage during file parsing
- Safe handling of user-provided file paths and URLs

The fuzzing implementation helps ensure robust parsing of potentially malicious or malformed dependency files.

### Signed Releases
All SuperBOM releases are cryptographically signed using Sigstore:
- **Keyless signing**: No long-term key management required
- **Transparency logs**: All signatures recorded in public logs  
- **Easy verification**: Simple commands to verify package integrity
- **SLSA provenance**: Build integrity and supply chain verification

See [RELEASE.md](RELEASE.md) for detailed verification instructions.
