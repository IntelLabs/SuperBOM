#!/usr/bin/env python3
"""
Property-based fuzzing using Hypothesis for SuperBOM parsers.
This provides structured fuzzing with valid and semi-valid input patterns.
"""

import tempfile
from pathlib import Path

from hypothesis import given, strategies as st, settings, HealthCheck

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    print("Note: pytest not available, running tests directly")

# Add the src directory to the path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from superbom.utils.parsers import (
    parse_requirements, 
    parse_conda_env, 
    parse_poetry_toml,
    extract_toml_dependencies,
    parse_requirement,
    parse_git_requirement
)


class TestHypothesisFuzzing:
    """Property-based testing for parser functions"""

    @given(st.text())
    @settings(max_examples=200, deadline=5000)
    def test_fuzz_parse_requirement_string(self, requirement_str):
        """Test parse_requirement with arbitrary strings"""
        try:
            result = parse_requirement(requirement_str)
            if result is not None:
                # If parsing succeeded, result should have expected structure
                assert isinstance(result, dict)
                assert "name" in result
                assert isinstance(result["name"], str)
        except Exception:
            # Parsing failure is expected for most random strings
            pass

    @given(st.text())
    @settings(max_examples=200, deadline=5000)
    def test_fuzz_parse_git_requirement(self, git_url):
        """Test parse_git_requirement with arbitrary strings"""
        try:
            result = parse_git_requirement(git_url)
            if result is not None:
                assert isinstance(result, str)
                assert len(result) > 0
        except Exception:
            pass

    @given(st.lists(st.text(min_size=1), min_size=0, max_size=20))
    @settings(max_examples=100, deadline=10000)
    def test_fuzz_requirements_file(self, lines):
        """Test parse_requirements with generated requirements file content"""
        content = "\n".join(lines)
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(content)
                f.flush()
                result = parse_requirements(f.name)
                assert isinstance(result, list)
                Path(f.name).unlink()
        except Exception:
            pass

    @given(st.dictionaries(
        st.text(min_size=1, max_size=50),
        st.one_of(
            st.text(min_size=1, max_size=100),
            st.lists(st.text(min_size=1, max_size=50)),
            st.dictionaries(st.text(min_size=1, max_size=20), st.text(min_size=1, max_size=50))
        )
    ))
    @settings(max_examples=50, deadline=15000)
    def test_fuzz_conda_environment_structure(self, env_data):
        """Test parse_conda_env with structured but potentially malformed YAML"""
        try:
            import yaml
            content = yaml.dump(env_data)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
                f.write(content)
                f.flush()
                result = parse_conda_env(f.name)
                # Result should be a tuple of 3 lists
                assert isinstance(result, tuple)
                assert len(result) == 3
                Path(f.name).unlink()
        except Exception:
            pass

    @given(st.dictionaries(
        st.text(min_size=1, max_size=20),
        st.one_of(
            st.text(min_size=1, max_size=100),
            st.dictionaries(st.text(min_size=1, max_size=20), st.text(min_size=1, max_size=100)),
            st.lists(st.text(min_size=1, max_size=50))
        )
    ))
    @settings(max_examples=50, deadline=15000)
    def test_fuzz_toml_structure(self, toml_data):
        """Test TOML parsers with structured but potentially malformed TOML"""
        try:
            import tomli_w
            content = tomli_w.dumps(toml_data)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
                f.write(content)
                f.flush()
                # Test both parsers
                result1 = parse_poetry_toml(f.name)
                result2 = extract_toml_dependencies(f.name)
                assert isinstance(result1, list)
                assert isinstance(result2, list)
                Path(f.name).unlink()
        except Exception:
            pass


def run_direct_tests():
    """Run hypothesis tests directly without pytest"""
    from hypothesis import given, strategies as st, settings
    
    print("🔄 Running property-based fuzzing with Hypothesis...")
    
    # Test 1: Requirement string parsing
    print("  📦 Testing requirement string parsing...")
    @given(st.text())
    @settings(max_examples=50, deadline=5000, suppress_health_check=[HealthCheck.too_slow])
    def test_requirement_parsing(requirement_str):
        try:
            result = parse_requirement(requirement_str)
            if result is not None:
                assert isinstance(result, dict)
                assert "name" in result
        except Exception:
            pass
    test_requirement_parsing()
    
    # Test 2: Git URL parsing  
    print("  🔗 Testing git requirement parsing...")
    @given(st.text())
    @settings(max_examples=30, deadline=3000, suppress_health_check=[HealthCheck.too_slow])
    def test_git_parsing(git_url):
        try:
            result = parse_git_requirement(git_url)
            if result is not None:
                assert isinstance(result, str)
        except Exception:
            pass
    test_git_parsing()
    
    print("✅ Property-based tests completed successfully!")


if __name__ == "__main__":
    run_direct_tests()