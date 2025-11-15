# MCP Server Test Suite

Comprehensive test coverage for the LangChain + Ollama + MCP system.

## Test Organization

### 1. **Unit Tests** (`test_unit_tools.py`)
Tests individual functions/components in isolation. Fast, many small assertions.

**Coverage:**
- Calculator tool (addition, subtraction, multiplication, division, edge cases)
- Weather tool (all units, invalid cities, case handling)
- Gold price tool (all currencies, formatting)
- Email tool (validation, special characters)
- Code executor tool (multiple languages, error handling)
- Web scraper tool (various URLs, invalid input)
- File operations tool (read, write, list, error handling)

**Run:** `python run_tests.py unit`

### 2. **Integration Tests** (`test_integration.py`)
Tests how different components work together (DB + API, service A + service B).

**Coverage:**
- AsyncClientManager + Flask integration
- RAG System + ChromaDB integration
- MCP Client + Server integration
- Flask API integration
- Tool chaining (multiple tools working together)
- Database locking prevention

**Run:** `python run_tests.py integration`

### 3. **End-to-End Tests** (`test_e2e.py`)
Simulates real user flows in the system (login → query → response).

**Coverage:**
- Complete query flow: Browser → Flask → AsyncManager → MCP Client → Ollama → MCP Server → Tools → Response
- RAG document upload and query flow
- Multi-tool combination flows
- Error handling flows
- Concurrent user flows
- UI interaction flows

**Run:** `python run_tests.py e2e`

**Note:** Requires Flask server to be running on http://localhost:5000

### 4. **API Tests** (`test_api.py`)
Validates endpoints, input validation, error handling, and contract stability.

**Coverage:**
- `/api/query` endpoint (all HTTP methods, input validation, error cases)
- `/api/rag/upload` endpoint (file upload, size limits, type validation)
- `/api/rag/query` endpoint (RAG queries, validation)
- Health/status endpoints
- HTTP method restrictions
- Rate limiting (if implemented)
- Error response formats
- CORS headers

**Run:** `python run_tests.py api`

**Note:** Requires Flask server to be running

### 5. **Regression Tests** (`test_regression.py`)
Guards against previously fixed bugs to ensure they don't reoccur.

**Coverage:**
- Database locking issue (MCP server must use HTTP API, not direct ChromaDB)
- Calculator edge cases (division by zero, floating point precision, large numbers)
- Weather tool issues (invalid cities, unit conversion)
- RAG system issues (empty docs, Unicode, duplicates)
- AsyncManager issues (memory leaks, thread safety)
- Code executor issues (infinite loops, malicious code, output capture)
- Email tool issues (invalid emails, special characters)
- File operations issues (path traversal, nonexistent files)
- Web scraper issues (invalid URLs, timeouts)

**Run:** `python run_tests.py regression`

## Quick Start

### Install Dependencies

```bash
pip install -r requirements-test.txt
```

Or use the test runner:

```bash
python run_tests.py --install-deps
```

### Run All Tests

```bash
python run_tests.py
```

### Run Specific Test Suite

```bash
python run_tests.py unit          # Unit tests only
python run_tests.py integration   # Integration tests
python run_tests.py e2e           # E2E tests (requires server)
python run_tests.py api           # API tests (requires server)
python run_tests.py regression    # Regression tests
```

### Run with Coverage

```bash
python run_tests.py --coverage
```

This generates:
- Terminal coverage report
- HTML coverage report in `htmlcov/index.html`

### Run with Verbose Output

```bash
python run_tests.py -v
```

## Using pytest Directly

### Run all tests

```bash
pytest
```

### Run specific test file

```bash
pytest tests/test_unit_tools.py
```

### Run specific test class

```bash
pytest tests/test_unit_tools.py::TestCalculatorTool
```

### Run specific test function

```bash
pytest tests/test_unit_tools.py::TestCalculatorTool::test_addition
```

### Run with markers

```bash
pytest -m unit              # Run only unit tests
pytest -m "not slow"        # Skip slow tests
pytest -m "integration"     # Run only integration tests
```

### Parallel execution

```bash
pytest -n auto              # Auto-detect CPU count
pytest -n 4                 # Use 4 workers
```

## Test Requirements

### For Unit Tests
- No external dependencies required
- Tests run in isolation

### For Integration Tests
- ChromaDB must be available (temporary databases used)
- AsyncClientManager must be functional

### For E2E and API Tests
- Flask web server must be running: `python web_server.py`
- Server should be accessible at `http://localhost:5000`
- All MCP components must be operational

## Test Data

Tests use:
- **Fixtures** for reusable test data (pytest fixtures)
- **Temporary files/directories** for file operations (pytest tmp_path)
- **Mocking** for external services where appropriate
- **Simulated responses** for weather, gold price, etc.

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt

    - name: Run unit tests
      run: pytest tests/test_unit_tools.py -v

    - name: Run integration tests
      run: pytest tests/test_integration.py -v

    - name: Run regression tests
      run: pytest tests/test_regression.py -v
```

## Writing New Tests

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Example Unit Test

```python
import pytest
from mcp_server import MCPServer

class TestMyNewTool:
    @pytest.fixture
    def server(self):
        return MCPServer()

    @pytest.mark.asyncio
    async def test_my_tool_basic(self, server):
        """Test basic functionality"""
        result = await server.my_new_tool({"param": "value"})
        assert "expected" in result[0].text

    @pytest.mark.asyncio
    async def test_my_tool_error_handling(self, server):
        """Test error handling"""
        result = await server.my_new_tool({"invalid": "data"})
        assert "error" in result[0].text.lower()
```

### Example Integration Test

```python
@pytest.mark.asyncio
async def test_component_integration():
    """Test two components working together"""
    from component_a import ComponentA
    from component_b import ComponentB

    comp_a = ComponentA()
    comp_b = ComponentB()

    # Test interaction
    data = await comp_a.get_data()
    result = await comp_b.process(data)

    assert result is not None
```

## Coverage Goals

- **Unit Tests**: 90%+ coverage
- **Integration Tests**: Critical paths covered
- **E2E Tests**: All major user flows
- **API Tests**: All endpoints validated
- **Regression Tests**: All known bugs covered

## Troubleshooting

### Tests fail with "Flask server not running"

**Solution:** Start the web server before running E2E/API tests:

```bash
python web_server.py
```

Then in another terminal:

```bash
python run_tests.py e2e
```

### Tests fail with "Ollama not available"

**Solution:** Some tests require Ollama. Either:
1. Start Ollama: `ollama serve`
2. Skip those tests: `pytest -m "not slow"`

### Import errors

**Solution:** Ensure you're running from the project root and dependencies are installed:

```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
```

## Test Metrics

After running tests with coverage:

```bash
python run_tests.py --coverage
```

View the HTML report:

```bash
open htmlcov/index.html
```

## Best Practices

1. **Keep tests fast**: Unit tests should run in milliseconds
2. **Use fixtures**: Reuse setup code with pytest fixtures
3. **Test edge cases**: Don't just test happy paths
4. **Clear assertions**: Make it obvious what's being tested
5. **Descriptive names**: Test names should describe what they test
6. **Independent tests**: Tests should not depend on each other
7. **Clean up**: Always clean up resources (use fixtures and context managers)

## Contact

For questions about tests, see the main project README or open an issue.
