# Changelog

All notable changes to SuperBOM will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive fuzzing suite for OSSF Scorecard compliance
  - Random input fuzzing with `fuzz/fuzz_parsers.py`
  - Property-based testing with Hypothesis in `fuzz/fuzz_hypothesis.py`
  - Interactive fuzzing runner `fuzz/run_fuzzing.sh`
  - GitHub Actions fuzzing workflow for CI/CD
- Signed releases using Sigstore/cosign for cryptographic verification
  - Automated release workflow with signature generation
  - SLSA Level 3 provenance for supply chain security
  - Release verification documentation
- Migrated from Poetry to uv package manager
  - Faster dependency resolution and installation
  - Modern PEP 621 project configuration
  - Improved development workflow
- Enhanced security documentation
  - Updated SECURITY.md with fuzzing information
  - Added RELEASE.md with signed release documentation
  - Comprehensive verification instructions

### Changed
- **BREAKING**: Replaced Poetry Factory with custom Dependency class
  - Removed dependency on `poetry-core`
  - Added support for standard Python packaging tools
  - Improved parsing accuracy and error handling
- Updated GitHub Actions workflow to use uv
  - Multi-version Python testing (3.11-3.13)
  - Improved CI/CD performance and reliability
- Modernized project configuration
  - Migrated to PEP 621 format in pyproject.toml
  - Updated dependency specifications
  - Added optional dependency groups for fuzzing and testing

### Fixed
- Argument parsing validation in main CLI
  - Fixed order of operations for file validation
  - Improved error messages and help text
- Parser robustness improvements
  - Better handling of malformed requirements
  - Enhanced error reporting for debugging
  - Graceful degradation for invalid inputs

### Security
- Added continuous security fuzzing
- Implemented signed releases with cryptographic verification
- Enhanced input validation and error handling
- Added SLSA provenance for build integrity

## [0.3.0] - 2024-XX-XX

### Added
- Initial SuperBOM release with core functionality
- Support for parsing requirements.txt files
- Support for parsing conda environment files
- Support for parsing pyproject.toml files
- GitHub repository analysis and license detection
- CLI interface with comprehensive options

### Features
- Multi-format dependency parsing
- License and vulnerability scanning
- SPDX and CycloneDX SBOM generation
- GitHub integration for repository analysis

---

## Version Numbering

SuperBOM follows [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes that require user action
- **MINOR**: New features that are backwards compatible
- **PATCH**: Bug fixes and security updates

## Release Process

1. Update this CHANGELOG.md with all changes
2. Update version in pyproject.toml
3. Commit changes: `git commit -m "Release vX.Y.Z"`
4. Create annotated tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
5. Push changes and tag: `git push origin main && git push origin vX.Y.Z`
6. GitHub Actions will automatically create signed release

For more details, see [RELEASE.md](RELEASE.md).