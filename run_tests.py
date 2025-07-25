#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("PASSED")
        else:
            print(f"FAILED (exit code: {result.returncode})")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    print("ResumeRoast Test Runner")
    
    if len(sys.argv) < 2:
        print("""
Usage: python run_tests.py [command]

Available commands:
  unit        - Run unit tests only (fast, no API calls)
  integration - Run integration tests (may require API keys)
  all         - Run all tests
  coverage    - Run tests with coverage report
  quick       - Run quick validation tests
  legacy      - Run legacy test scripts
  
Examples:
  python run_tests.py unit
  python run_tests.py all
  python run_tests.py coverage
        """)
        return
    
    command = sys.argv[1].lower()
    
    # Check if pytest is available
    try:
        subprocess.run(['pytest', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("pytest not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pytest', 'pytest-cov'])
    
    if command == 'unit':
        run_command(['pytest', 'tests/', '-m', 'not integration', '-v'], 
                   "Running Unit Tests")
    
    elif command == 'integration':
        run_command(['pytest', 'tests/test_integration.py', '-v'], 
                   "Running Integration Tests")
    
    elif command == 'all':
        success1 = run_command(['pytest', 'tests/', '-v'], 
                              "Running All Tests")
        if success1:
            print("\nAll tests completed successfully!")
        else:
            print("\nSome tests failed. Check output above.")
    
    elif command == 'coverage':
        run_command(['pytest', 'tests/', '--cov=utils', '--cov-report=html', '--cov-report=term', '-v'], 
                   "Running Tests with Coverage")
        print("\nCoverage report generated in htmlcov/index.html")
    
    elif command == 'quick':
        run_command(['pytest', 'tests/test_resume_parser.py::TestResumeParser::test_parser_initialization', '-v'], 
                   "Quick Validation Test")
    
    elif command == 'legacy':
        print("\nRunning Legacy Test Scripts")
        success1 = run_command([sys.executable, 'test_openai_extraction.py'], 
                              "OpenAI Extraction Test")
        if os.getenv('GOOGLE_API_KEY'):
            success2 = run_command([sys.executable, 'test_dual_model.py'], 
                                  "Dual Model Test")
        else:
            print("Skipping dual model test (GOOGLE_API_KEY not set)")
            success2 = True
        
        if success1 and success2:
            print("\nLegacy tests completed successfully!")
        else:
            print("\nSome legacy tests failed.")
    
    else:
        print(f"Unknown command: {command}")
        print("Use 'python run_tests.py' without arguments to see available commands.")

if __name__ == '__main__':
    main()
