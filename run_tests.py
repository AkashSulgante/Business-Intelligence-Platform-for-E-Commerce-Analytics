#!/usr/bin/env python3
"""
Script to run all tests for the E-commerce BI Platform.
"""

import subprocess
import sys
from pathlib import Path

def run_tests():
    """Run all tests using pytest."""
    project_root = Path(__file__).parent
    print("Running tests for E-commerce BI Platform...")
    print("=" * 50)

    try:
        # Run pytest with verbose output
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short"
        ], cwd=project_root, capture_output=True, text=True)

        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        print("=" * 50)
        if result.returncode == 0:
            print("All tests passed!")
        else:
            print(f"Tests failed with exit code: {result.returncode}")

        return result.returncode

    except FileNotFoundError:
        print("Error: pytest not found. Please install test dependencies:")
        print("pip install -r tests/requirements.txt")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

def run_specific_test(test_module):
    """Run a specific test module."""
    project_root = Path(__file__).parent
    print(f"Running tests for {test_module}...")
    print("=" * 50)

    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            f"tests/test_{test_module}.py",
            "-v",
            "--tb=short"
        ], cwd=project_root, capture_output=True, text=True)

        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        print("=" * 50)
        if result.returncode == 0:
            print(f"All tests in {test_module} passed!")
        else:
            print(f"Tests in {test_module} failed with exit code: {result.returncode}")

        return result.returncode

    except FileNotFoundError:
        print("Error: pytest not found. Please install test dependencies:")
        print("pip install -r tests/requirements.txt")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test module
        module_name = sys.argv[1]
        sys.exit(run_specific_test(module_name))
    else:
        # Run all tests
        sys.exit(run_tests())