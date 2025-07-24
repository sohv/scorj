# Testing Guide for ResumeRoast

This document provides comprehensive instructions for running tests in the ResumeRoast project.

## Overview

ResumeRoast includes multiple testing approaches:
- **Legacy test scripts** (Recommended - fully functional)
- **Pytest framework** (Unit and integration tests)
- **Manual API testing** (Backend validation)
- **Test runner script** (Unified test execution)

## Quick Start

The easiest way to run tests is using the test runner script:

```bash
python run_tests.py legacy
```

This will run the fully functional legacy test scripts that validate the core scoring functionality.

## Available Test Commands

### Test Runner Script

The `run_tests.py` script provides a unified interface for all testing options:

```bash
python run_tests.py [command]
```

**Available commands:**

| Command | Description | Status |
|---------|-------------|---------|
| `legacy` | Run legacy test scripts | ✅ **Recommended** |
| `unit` | Run unit tests only (no API calls) | Needs fixes |
| `integration` | Run integration tests | Requires API keys |
| `all` | Run all pytest tests | Needs fixes |
| `coverage` | Run tests with coverage report | Framework ready |
| `quick` | Quick validation test | ✅ Working |

### Examples

```bash
# Run working legacy tests (recommended)
python run_tests.py legacy

# Run quick validation
python run_tests.py quick

# Run all tests (may have failures)
python run_tests.py all

# Generate coverage report
python run_tests.py coverage
```

## Legacy Test Scripts (Recommended)

These are fully functional test scripts that validate core functionality:

### 1. OpenAI Scoring Engine Test

```bash
python test_openai_extraction.py
```

**What it tests:**
- Resume parsing functionality
- Job description parsing
- OpenAI-based scoring algorithm
- Score breakdown and analysis
- Transparency metrics

**Expected output:**
```
Enhanced Scoring Engine Test
========================================
Testing Enhanced Scoring Engine...
Parsing resume...
Resume parsed. Skills found: 11
Parsing job description...
Job parsed. Skills found: 16
Calculating enhanced score...

SCORING RESULTS
==================================================
Overall Score: 82/100
Confidence Level: High
Match Category: Good match with minor gaps
...
```

### 2. Dual Model Test

```bash
python test_dual_model.py
```

**Requirements:** `GOOGLE_API_KEY` environment variable must be set.

**What it tests:**
- Dual-model scoring (OpenAI + Gemini)
- Model consensus analysis
- Score variance calculation
- Fallback mechanisms

## Pytest Framework Tests

The project includes a comprehensive pytest framework (some tests need minor fixes):

### Running Specific Tests

```bash
# Test parser initialization
pytest tests/test_resume_parser.py::TestResumeParser::test_parser_initialization -v

# Test base scoring engine
pytest tests/test_scoring_engines.py::TestBaseScoringEngine -v

# Run all tests in a file
pytest tests/test_scoring_engines.py -v
```

### Test Categories

#### 1. Unit Tests
- **Resume Parser Tests**: `tests/test_resume_parser.py`
- **Job Parser Tests**: `tests/test_job_parser.py`
- **Scoring Engine Tests**: `tests/test_scoring_engines.py`

#### 2. Integration Tests
- **End-to-End Workflow**: `tests/test_integration.py`

### Test Structure

```
tests/
├── __init__.py
├── test_resume_parser.py      # Resume parsing tests
├── test_job_parser.py         # Job description parsing tests
├── test_scoring_engines.py    # Scoring algorithm tests
└── test_integration.py        # End-to-end workflow tests
```

## Manual API Testing

Test the backend API endpoints directly:

### 1. Health Check

```bash
curl http://localhost:8000/
```

**Expected response:**
```json
{"status": "healthy", "message": "ResumeRoast API is running"}
```

### 2. AI Chat Endpoint

```bash
curl -X POST "http://localhost:8000/ai/chat" \
     -F "question=Hello, can you help me understand scoring?" \
     -F "model=openai"
```

**Expected response:**
```json
{
  "response": "Absolutely! Resume scoring is a method used...",
  "model_used": "openai",
  "success": true
}
```

### 3. Available Models

```bash
curl http://localhost:8000/models
```

## Environment Setup

### Required Environment Variables

```bash
# Required for OpenAI features
export OPENAI_API_KEY="your_openai_api_key"

# Required for Gemini/dual-model features
export GOOGLE_API_KEY="your_google_api_key"

# Optional - API URL override
export API_URL="http://localhost:8000"
```

### Installing Test Dependencies

Tests require these packages (included in `requirements.txt`):

```bash
pip install pytest pytest-asyncio pytest-cov
```

## Test Results Interpretation

### ✅ Passing Tests
- **OpenAI scoring engine**: Core functionality working
- **Backend API endpoints**: All endpoints responsive
- **AI chat functionality**: Interactive features working
- **Base scoring engine**: Utility functions working

### ⚠️ Tests Requiring Setup
- **Dual model tests**: Need `GOOGLE_API_KEY`
- **Integration tests**: Need both API keys
- **Coverage reports**: Need `pytest-cov`

### Tests Needing Fixes
- Some pytest unit tests need minor API structure alignment
- Mock tests need updated response formats

## Troubleshooting

### Common Issues

#### 1. "pytest not found"
```bash
pip install pytest pytest-asyncio pytest-cov
```

#### 2. "OpenAI API key not found"
```bash
export OPENAI_API_KEY="your_key_here"
```

#### 3. "Backend connection failed"
Make sure the backend is running:
```bash
cd backend
uvicorn main:app --reload
```

#### 4. "Google API key not set"
For dual-model tests:
```bash
export GOOGLE_API_KEY="your_google_key_here"
```

### Debugging Tips

1. **Check environment variables:**
   ```bash
   echo $OPENAI_API_KEY
   echo $GOOGLE_API_KEY
   ```

2. **Verify backend is running:**
   ```bash
   curl http://localhost:8000/
   ```

3. **Check test output files:**
   - Legacy tests create `test_scoring_results.json`
   - Coverage reports create `htmlcov/index.html`

4. **Run with verbose output:**
   ```bash
   python run_tests.py legacy -v
   pytest tests/ -v
   ```

## Test Configuration

### Pytest Configuration

The project includes `pytest.ini` with optimized settings:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
```

### Test Markers

Tests can be marked for selective execution:

```bash
# Run only unit tests (no API calls)
pytest -m "not integration"

# Run only integration tests
pytest -m integration

# Run only fast tests
pytest -m "not slow"
```

## Coverage Reports

Generate code coverage reports:

```bash
python run_tests.py coverage
```

This creates:
- Terminal coverage report
- HTML report in `htmlcov/index.html`

## Continuous Integration

For CI/CD pipelines, use:

```bash
# Basic validation (no API keys required)
python run_tests.py quick

# Full test suite (requires API keys)
python run_tests.py legacy
```

## Best Practices

1. **Start with legacy tests** - they're guaranteed to work
2. **Set up environment variables** before running tests
3. **Ensure backend is running** for API tests
4. **Use the test runner script** for consistent execution
5. **Check coverage reports** to identify untested code

## Getting Help

If tests fail:

1. Check this documentation for troubleshooting steps
2. Verify environment setup
3. Ensure all dependencies are installed
4. Check backend server status
5. Review test output for specific error messages

---

**Last Updated:** July 20, 2025  
**Project:** ResumeRoast  
**Test Framework:** pytest + legacy scripts
