# Release Process and Signed Releases

SuperBOM uses cryptographically signed releases to ensure the integrity and authenticity of distributed software packages.

## 🔒 Signed Releases

All SuperBOM releases are signed using [Sigstore](https://www.sigstore.dev/), providing:
- **Keyless signing**: No need to manage long-term keys
- **Transparency**: All signatures logged in public transparency log
- **Verification**: Easy verification of package integrity

## 📋 Release Process

### Automated Release (Recommended)

1. **Create a version tag**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **GitHub Actions will automatically**:
   - Run all tests and fuzzing
   - Build the package
   - Sign all artifacts with cosign
   - Create a GitHub release
   - Upload signed artifacts
   - Generate SLSA provenance
   - Publish to PyPI (if configured)

### Manual Release

You can also trigger a release manually:
1. Go to the "Actions" tab in GitHub
2. Select "Release and Sign" workflow
3. Click "Run workflow"
4. Enter the tag name (e.g., `v1.0.0`)

## 🔍 Verifying Releases

### Verify GitHub Release Artifacts

1. **Download the release and signature bundle**:
   ```bash
   curl -L -o superbom-1.0.0.tar.gz https://github.com/IntelLabs/SuperBOM/releases/download/v1.0.0/superbom-1.0.0.tar.gz
   curl -L -o superbom-1.0.0.tar.gz.bundle https://github.com/IntelLabs/SuperBOM/releases/download/v1.0.0/superbom-1.0.0.tar.gz.bundle
   ```

2. **Install cosign**:
   ```bash
   # macOS
   brew install cosign
   
   # Linux
   curl -O -L "https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64"
   sudo mv cosign-linux-amd64 /usr/local/bin/cosign
   sudo chmod +x /usr/local/bin/cosign
   ```

3. **Verify the signature**:
   ```bash
   cosign verify-blob --bundle superbom-1.0.0.tar.gz.bundle superbom-1.0.0.tar.gz
   ```

### Verify PyPI Package

1. **Download from PyPI**:
   ```bash
   pip download --no-deps superbom==1.0.0
   ```

2. **Verify signature** (if available):
   ```bash
   cosign verify-blob --bundle superbom-1.0.0-py3-none-any.whl.sig superbom-1.0.0-py3-none-any.whl
   ```

## 🛡️ SLSA Provenance

SuperBOM releases include SLSA (Supply Chain Levels for Software Artifacts) Level 3 provenance, which provides:

- **Build system integrity**: Verification that the package was built in the expected environment
- **Source integrity**: Confirmation that the build corresponds to the expected source code
- **Reproducible builds**: Evidence of the build process and environment

### Verify SLSA Provenance

1. **Install slsa-verifier**:
   ```bash
   go install github.com/slsa-framework/slsa-verifier/v2/cmd/slsa-verifier@latest
   ```

2. **Verify provenance**:
   ```bash
   slsa-verifier verify-artifact superbom-1.0.0.tar.gz \
     --provenance-path superbom-1.0.0.tar.gz.intoto.jsonl \
     --source-uri github.com/IntelLabs/SuperBOM
   ```

## 🏷️ Version Tagging

SuperBOM follows [Semantic Versioning](https://semver.org/):
- **Major version** (`v2.0.0`): Breaking changes
- **Minor version** (`v1.1.0`): New features, backwards compatible
- **Patch version** (`v1.0.1`): Bug fixes, backwards compatible

### Creating a Release

1. **Update version in pyproject.toml**:
   ```toml
   [project]
   version = "1.0.0"
   ```

2. **Update CHANGELOG.md** with release notes

3. **Commit changes**:
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "Release v1.0.0"
   ```

4. **Create and push tag**:
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin main
   git push origin v1.0.0
   ```

## 🔧 Configuration

### Required Secrets

For automated releases to work, configure these GitHub secrets:

1. **PYPI_API_TOKEN**: PyPI API token for publishing packages
   - Go to PyPI → Account Settings → API tokens
   - Create a token for the SuperBOM project
   - Add as a repository secret

### Release Environment

The workflow uses a `release` environment for additional protection:
- Configure branch protection rules
- Add required reviewers for release approval
- Set up deployment protection rules

## 📊 OSSF Scorecard Impact

Signed releases improve your OSSF Scorecard rating by:
- ✅ **Signed-Releases**: Cryptographically signed release artifacts
- ✅ **Binary-Artifacts**: Clean source-only releases
- ✅ **Packaging**: Automated and secure packaging process
- ✅ **Token-Permissions**: Minimal required permissions
- ✅ **Dangerous-Workflow**: Secure workflow patterns

## 🔍 Troubleshooting

### Cosign Issues

If signature verification fails:
1. Ensure you have the latest version of cosign
2. Check that the bundle file is properly downloaded
3. Verify the artifact hasn't been tampered with

### Release Workflow Issues

If the release workflow fails:
1. Check that the tag follows the `v*` pattern
2. Ensure all tests pass before creating the tag
3. Verify repository permissions for the GitHub token

### SLSA Provenance Issues

If SLSA verification fails:
1. Ensure the slsa-verifier tool is properly installed
2. Check that the provenance file exists in the release
3. Verify the source URI matches your repository

For additional help, see the [GitHub Issues](https://github.com/IntelLabs/SuperBOM/issues) or the [OSSF Scorecard documentation](https://github.com/ossf/scorecard).