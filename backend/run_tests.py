#!/usr/bin/env python3
"""
Simple test runner for StackAI backend unit tests.
"""

import sys
import subprocess


def run_command(cmd):
    """Run a command and return the exit code."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Main test runner."""
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py [unit|all]")
        print("")
        print("Commands:")
        print("  unit        Run unit tests only (fast)")
        print("  all         Run all tests")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "unit":
        exit_code = run_command(["python", "-m", "pytest", "tests/unit/"])
    elif command == "all":
        exit_code = run_command(["python", "-m", "pytest", "tests/"])
    else:
        print(f"Unknown command: {command}")
        print("Available commands: unit, all")
        sys.exit(1)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 