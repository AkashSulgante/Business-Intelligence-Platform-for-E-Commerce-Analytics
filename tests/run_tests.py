#!/usr/bin/env python3
"""
Test runner for the E-commerce BI Platform.
Runs all unit tests and provides a summary.
"""

import unittest
import sys
import os
from pathlib import Path

def run_tests():
    """Run all test modules."""
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = project_root / 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests())