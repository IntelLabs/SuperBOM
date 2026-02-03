#!/bin/bash
#
# Helper script to create a new SuperBOM release
# This script automates the release process with proper validation
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Check if we're on main branch
check_branch() {
    local current_branch=$(git rev-parse --abbrev-ref HEAD)
    if [ "$current_branch" != "main" ]; then
        log_error "Must be on main branch to create a release. Current branch: $current_branch"
        exit 1
    fi
    log_success "On main branch"
}

# Check if working directory is clean
check_clean() {
    if [ -n "$(git status --porcelain)" ]; then
        log_error "Working directory is not clean. Please commit or stash changes."
        git status --short
        exit 1
    fi
    log_success "Working directory is clean"
}

# Validate version format
validate_version() {
    local version=$1
    if [[ ! $version =~ ^v?[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        log_error "Invalid version format. Expected: vX.Y.Z (e.g., v1.0.0)"
        exit 1
    fi
    
    # Ensure version starts with 'v'
    if [[ ! $version =~ ^v ]]; then
        version="v$version"
    fi
    
    echo "$version"
}

# Check if version already exists
check_version_exists() {
    local version=$1
    if git tag -l | grep -q "^$version$"; then
        log_error "Version $version already exists"
        exit 1
    fi
    log_success "Version $version is available"
}

# Update version in pyproject.toml
update_version() {
    local version=$1
    local clean_version=${version#v}  # Remove 'v' prefix
    
    log_info "Updating version in pyproject.toml to $clean_version"
    
    # Update version using sed (cross-platform compatible)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/^version = .*/version = \"$clean_version\"/" pyproject.toml
    else
        # Linux
        sed -i "s/^version = .*/version = \"$clean_version\"/" pyproject.toml
    fi
    
    log_success "Updated version in pyproject.toml"
}

# Run tests to ensure everything is working
run_tests() {
    log_info "Running tests..."
    if ! uv run pytest; then
        log_error "Tests failed. Cannot create release."
        exit 1
    fi
    log_success "All tests passed"
}

# Build the package to ensure it builds correctly
build_package() {
    log_info "Building package..."
    if ! uv build; then
        log_error "Package build failed. Cannot create release."
        exit 1
    fi
    log_success "Package built successfully"
}

# Create release commit and tag
create_release() {
    local version=$1
    
    log_info "Creating release commit and tag for $version"
    
    # Add changed files
    git add pyproject.toml CHANGELOG.md
    
    # Create release commit
    git commit -m "Release $version"
    
    # Create annotated tag
    git tag -a "$version" -m "Release $version"
    
    log_success "Created commit and tag for $version"
}

# Push changes and trigger release
push_release() {
    local version=$1
    
    log_info "Pushing changes and tag to origin..."
    
    # Push main branch
    git push origin main
    
    # Push tag (this will trigger the release workflow)
    git push origin "$version"
    
    log_success "Pushed changes and tag"
    log_info "Release workflow will start automatically on GitHub"
    log_info "View progress at: https://github.com/IntelLabs/SuperBOM/actions"
}

# Main function
main() {
    echo -e "${BLUE}┌──────────────────────────────────────┐${NC}"
    echo -e "${BLUE}│      SuperBOM Release Creator        │${NC}"
    echo -e "${BLUE}└──────────────────────────────────────┘${NC}"
    echo ""
    
    # Get version from user if not provided
    if [ -z "$1" ]; then
        echo "Enter the version to release (e.g., v1.0.0):"
        read -r version
    else
        version=$1
    fi
    
    # Validate and normalize version
    version=$(validate_version "$version")
    
    log_info "Creating release for version: $version"
    echo ""
    
    # Pre-flight checks
    log_info "Running pre-flight checks..."
    check_branch
    check_clean
    check_version_exists "$version"
    echo ""
    
    # Remind user to update CHANGELOG
    log_warning "Have you updated CHANGELOG.md with release notes for $version?"
    read -p "Continue? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Please update CHANGELOG.md and re-run this script"
        exit 0
    fi
    echo ""
    
    # Update version
    update_version "$version"
    echo ""
    
    # Test and build
    run_tests
    echo ""
    build_package
    echo ""
    
    # Create release
    create_release "$version"
    echo ""
    
    # Final confirmation
    log_warning "Ready to push $version to GitHub (this will trigger the release workflow)"
    read -p "Continue? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Release created locally. You can push manually with:"
        echo "  git push origin main && git push origin $version"
        exit 0
    fi
    echo ""
    
    # Push release
    push_release "$version"
    echo ""
    
    log_success "Release $version created successfully! 🎉"
    log_info "The GitHub Actions workflow will:"
    log_info "  • Build and sign the release artifacts"
    log_info "  • Create a GitHub release"  
    log_info "  • Generate SLSA provenance"
    log_info "  • Publish to PyPI (if configured)"
    echo ""
    log_info "Monitor progress: https://github.com/IntelLabs/SuperBOM/actions"
}

# Show usage if --help is passed
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [version]"
    echo ""
    echo "Create a new signed release for SuperBOM"
    echo ""
    echo "Arguments:"
    echo "  version    Version to release (e.g., v1.0.0). Optional - will prompt if not provided."
    echo ""
    echo "Examples:"
    echo "  $0 v1.0.0    # Create release v1.0.0"
    echo "  $0           # Interactive mode"
    echo ""
    echo "This script will:"
    echo "  • Validate you're on main branch with clean working directory"
    echo "  • Update version in pyproject.toml"
    echo "  • Run tests and build package"
    echo "  • Create release commit and tag"
    echo "  • Push to GitHub to trigger signed release workflow"
    exit 0
fi

# Run main function
main "$@"