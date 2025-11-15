#!/usr/bin/env python3
"""
Test Runner for MCP Server
Runs all test suites with proper reporting
"""
import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type="all", verbose=False, coverage=False):
    """Run tests with specified configuration"""

    test_dir = Path(__file__).parent / "tests"

    # Map test types to files
    test_files = {
        "unit": "test_unit_tools.py",
        "integration": "test_integration.py",
        "e2e": "test_e2e.py",
        "api": "test_api.py",
        "regression": "test_regression.py",
        "all": ""  # Run all tests
    }

    if test_type not in test_files:
        print(f"❌ Invalid test type: {test_type}")
        print(f"   Valid types: {', '.join(test_files.keys())}")
        return 1

    # Build pytest command
    cmd = ["pytest"]

    if test_type == "all":
        cmd.append(str(test_dir))
    else:
        cmd.append(str(test_dir / test_files[test_type]))

    # Add flags
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")

    cmd.append("--tb=short")
    cmd.append("-ra")  # Show summary of all test outcomes

    if coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])

    # Add markers
    cmd.append("-m")
    cmd.append("not slow")  # Skip slow tests by default

    print("=" * 70)
    print(f"🧪 Running {test_type.upper()} Tests")
    print("=" * 70)
    print(f"Command: {' '.join(cmd)}")
    print()

    # Run tests
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        return result.returncode
    except FileNotFoundError:
        print("\n❌ pytest not found. Install with:")
        print("   pip install pytest pytest-asyncio pytest-cov")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Run MCP Server tests")

    parser.add_argument(
        "test_type",
        nargs="?",
        default="all",
        choices=["all", "unit", "integration", "e2e", "api", "regression"],
        help="Type of tests to run (default: all)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )

    parser.add_argument(
        "-c", "--coverage",
        action="store_true",
        help="Generate coverage report"
    )

    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install test dependencies before running"
    )

    args = parser.parse_args()

    # Install dependencies if requested
    if args.install_deps:
        print("📦 Installing test dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "pytest", "pytest-asyncio", "pytest-cov", "requests"
        ])
        print()

    # Run tests
    exit_code = run_tests(args.test_type, args.verbose, args.coverage)

    # Summary
    print()
    print("=" * 70)
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print(f"❌ Tests failed with exit code: {exit_code}")
    print("=" * 70)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
