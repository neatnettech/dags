#!/usr/bin/env python3
"""
Test runner script with different test suites
"""
import subprocess
import sys
import argparse
import shutil


def run_tests(test_type="all", verbose=False, coverage=True):
    """Run tests based on type"""
    
    # Check if we should use poetry or pytest directly
    use_poetry = shutil.which("poetry") is not None
    pytest_available = shutil.which("pytest") is not None
    
    if use_poetry:
        cmd = ["poetry", "run", "pytest"]
    elif pytest_available:
        cmd = ["pytest"]
    else:
        print("Error: Neither Poetry nor pytest is available in PATH")
        print("Please install Poetry with: pip install poetry")
        print("Or install pytest with: pip install pytest")
        sys.exit(1)
    
    # Add verbosity
    if verbose:
        cmd.append("-vv")
    
    # Add coverage if requested
    if coverage:
        cmd.extend([
            "--cov=api",
            "--cov-report=term-missing",
            "--cov-report=html"
        ])
    
    # Select test type
    if test_type == "unit":
        cmd.extend(["-m", "unit", "tests/unit"])
    elif test_type == "api":
        cmd.extend(["-m", "api", "tests/api"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration", "tests/integration"])
    elif test_type == "fast":
        cmd.extend(["-m", "not slow"])
    elif test_type != "all":
        print(f"Unknown test type: {test_type}")
        sys.exit(1)
    
    # Run tests
    print(f"Running {test_type} tests...")
    print(f"Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print(f"\n✅ All {test_type} tests passed!")
    else:
        print(f"\n❌ Some {test_type} tests failed!")
    
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run test suites")
    parser.add_argument(
        "type",
        nargs="?",
        default="all",
        choices=["all", "unit", "api", "integration", "fast"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--no-cov",
        action="store_true",
        help="Disable coverage reporting"
    )
    
    args = parser.parse_args()
    
    sys.exit(run_tests(
        test_type=args.type,
        verbose=args.verbose,
        coverage=not args.no_cov
    ))


if __name__ == "__main__":
    main()