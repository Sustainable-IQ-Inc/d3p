#!/usr/bin/env python3
"""
Test runner script for the BEM Reports backend.
Provides convenient test execution with different options.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, check=True):
    """Run a command and handle errors"""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return e

def install_test_dependencies():
    """Install test dependencies if not present"""
    test_packages = [
        'pytest>=6.2.5',
        'pytest-cov>=4.0.0',
        'pytest-mock>=3.10.0',
        'pytest-asyncio>=0.21.0'
    ]
    
    print("Installing test dependencies...")
    for package in test_packages:
        cmd = [sys.executable, '-m', 'pip', 'install', package]
        run_command(cmd, check=False)

def run_tests(test_type="all", coverage=False, verbose=False, pattern=None, marker=None):
    """Run tests with specified options"""
    
    # Base pytest command
    cmd = [sys.executable, '-m', 'pytest']
    
    # Add verbosity
    if verbose:
        cmd.append('-vv')
    else:
        cmd.append('-v')
    
    # Add coverage if requested
    if coverage:
        cmd.extend(['--cov=.', '--cov-report=html', '--cov-report=term-missing'])
    
    # Add marker filter
    if marker:
        cmd.extend(['-m', marker])
    
    # Add test selection based on type
    if test_type == "unit":
        cmd.extend(['-m', 'unit'])
    elif test_type == "integration":
        cmd.extend(['-m', 'integration'])
    elif test_type == "api":
        cmd.extend(['-m', 'api'])
    elif test_type == "fast":
        cmd.extend(['-m', 'not slow'])
    
    # Add pattern matching
    if pattern:
        cmd.extend(['-k', pattern])
    
    # Add test directory
    cmd.append('tests/')
    
    return run_command(cmd)

def run_specific_test_file(test_file, coverage=False):
    """Run a specific test file"""
    cmd = [sys.executable, '-m', 'pytest', '-v']
    
    if coverage:
        cmd.extend(['--cov=.', '--cov-report=term-missing'])
    
    cmd.append(f'tests/{test_file}')
    
    return run_command(cmd)

def lint_tests():
    """Run linting on test files"""
    print("Running flake8 on test files...")
    cmd = [sys.executable, '-m', 'flake8', 'tests/', '--max-line-length=100']
    return run_command(cmd, check=False)

def main():
    parser = argparse.ArgumentParser(description='Run BEM Reports backend tests')
    parser.add_argument('--type', choices=['all', 'unit', 'integration', 'api', 'fast'], 
                       default='all', help='Type of tests to run')
    parser.add_argument('--coverage', action='store_true', 
                       help='Generate coverage report')
    parser.add_argument('--verbose', action='store_true', 
                       help='Verbose output')
    parser.add_argument('--pattern', type=str, 
                       help='Run tests matching pattern')
    parser.add_argument('--marker', type=str, 
                       help='Run tests with specific marker')
    parser.add_argument('--file', type=str, 
                       help='Run specific test file')
    parser.add_argument('--install-deps', action='store_true', 
                       help='Install test dependencies')
    parser.add_argument('--lint', action='store_true', 
                       help='Run linting on tests')
    
    args = parser.parse_args()
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    if args.install_deps:
        install_test_dependencies()
        return
    
    if args.lint:
        lint_tests()
        return
    
    if args.file:
        result = run_specific_test_file(args.file, args.coverage)
    else:
        result = run_tests(
            test_type=args.type,
            coverage=args.coverage,
            verbose=args.verbose,
            pattern=args.pattern,
            marker=args.marker
        )
    
    # Exit with the same code as pytest
    if hasattr(result, 'returncode'):
        sys.exit(result.returncode)

if __name__ == '__main__':
    main() 