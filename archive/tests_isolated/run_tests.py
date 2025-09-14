#!/usr/bin/env python3
"""
Standalone test runner for isolated test suite.
"""

import sys
import os
import subprocess
from pathlib import Path

def setup_test_environment():
    """Setup the test environment with proper paths."""
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Set environment variables
    os.environ['PYTHONPATH'] = str(project_root)
    os.environ['PYTEST_CURRENT_TEST'] = 'true'

def run_tests(test_type=None, verbose=True, coverage=False):
    """Run tests with specified options."""
    setup_test_environment()
    
    # Base pytest command
    cmd = ['python3', '-m', 'pytest']
    
    # Add test directory based on type
    if test_type == 'unit':
        cmd.append('unit/')
    elif test_type == 'integration':
        cmd.append('integration/')
    elif test_type == 'performance':
        cmd.append('performance/')
    else:
        cmd.append('.')  # Run all tests
    
    # Add options
    if verbose:
        cmd.append('-v')
    
    if coverage:
        cmd.extend(['--cov=engine', '--cov-report=html', '--cov-report=term'])
    
    # Add common options
    cmd.extend([
        '--tb=short',
        '--strict-markers',
        '--disable-warnings'
    ])
    
    print(f"Running command: {' '.join(cmd)}")
    print(f"Working directory: {os.getcwd()}")
    
    # Run tests
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run isolated test suite')
    parser.add_argument('--type', choices=['unit', 'integration', 'performance', 'all'], 
                       default='all', help='Test type to run')
    parser.add_argument('--no-verbose', action='store_true', help='Disable verbose output')
    parser.add_argument('--coverage', action='store_true', help='Run with coverage')
    
    args = parser.parse_args()
    
    test_type = None if args.type == 'all' else args.type
    verbose = not args.no_verbose
    
    exit_code = run_tests(test_type, verbose, args.coverage)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
