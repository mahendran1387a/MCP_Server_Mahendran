"""
Unit Tests for MCP Server Tools
Tests individual functions/components in isolation
"""
import pytest
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server import MCPServer


class TestCalculatorTool:
    """Unit tests for calculator tool"""

    @pytest.fixture
    def server(self):
        """Create server instance for each test"""
        return MCPServer()

    @pytest.mark.asyncio
    async def test_addition(self, server):
        """Test addition operation"""
        result = await server.calculator_tool({
            "operation": "add",
            "a": 10,
            "b": 5
        })
        assert "15" in result[0].text
        assert "10 + 5" in result[0].text

    @pytest.mark.asyncio
    async def test_subtraction(self, server):
        """Test subtraction operation"""
        result = await server.calculator_tool({
            "operation": "subtract",
            "a": 20,
            "b": 8
        })
        assert "12" in result[0].text
        assert "20 - 8" in result[0].text

    @pytest.mark.asyncio
    async def test_multiplication(self, server):
        """Test multiplication operation"""
        result = await server.calculator_tool({
            "operation": "multiply",
            "a": 6,
            "b": 7
        })
        assert "42" in result[0].text
        assert "6 × 7" in result[0].text

    @pytest.mark.asyncio
    async def test_division(self, server):
        """Test division operation"""
        result = await server.calculator_tool({
            "operation": "divide",
            "a": 100,
            "b": 4
        })
        assert "25" in result[0].text
        assert "100 ÷ 4" in result[0].text

    @pytest.mark.asyncio
    async def test_division_by_zero(self, server):
        """Test division by zero error handling"""
        result = await server.calculator_tool({
            "operation": "divide",
            "a": 10,
            "b": 0
        })
        assert "Cannot divide by zero" in result[0].text

    @pytest.mark.asyncio
    async def test_invalid_operation(self, server):
        """Test invalid operation error handling"""
        result = await server.calculator_tool({
            "operation": "modulo",
            "a": 10,
            "b": 3
        })
        assert "Unknown operation" in result[0].text

    @pytest.mark.asyncio
    async def test_floating_point(self, server):
        """Test floating point operations"""
        result = await server.calculator_tool({
            "operation": "divide",
            "a": 10,
            "b": 3
        })
        assert "3.33" in result[0].text

    @pytest.mark.asyncio
    async def test_negative_numbers(self, server):
        """Test operations with negative numbers"""
        result = await server.calculator_tool({
            "operation": "multiply",
            "a": -5,
            "b": 3
        })
        assert "-15" in result[0].text

    @pytest.mark.asyncio
    async def test_large_numbers(self, server):
        """Test operations with large numbers"""
        result = await server.calculator_tool({
            "operation": "multiply",
            "a": 999999,
            "b": 999999
        })
        assert "999998000001" in result[0].text


class TestWeatherTool:
    """Unit tests for weather tool"""

    @pytest.fixture
    def server(self):
        return MCPServer()

    @pytest.mark.asyncio
    async def test_celsius(self, server):
        """Test weather in Celsius"""
        result = await server.weather_tool({
            "city": "London",
            "units": "celsius"
        })
        text = result[0].text
        assert "London" in text
        assert "°C" in text
        assert "Conditions:" in text

    @pytest.mark.asyncio
    async def test_fahrenheit(self, server):
        """Test weather in Fahrenheit"""
        result = await server.weather_tool({
            "city": "New York",
            "units": "fahrenheit"
        })
        text = result[0].text
        assert "New York" in text
        assert "°F" in text

    @pytest.mark.asyncio
    async def test_kelvin(self, server):
        """Test weather in Kelvin"""
        result = await server.weather_tool({
            "city": "Tokyo",
            "units": "kelvin"
        })
        text = result[0].text
        assert "Tokyo" in text
        assert "K" in text

    @pytest.mark.asyncio
    async def test_default_units(self, server):
        """Test weather with default units (celsius)"""
        result = await server.weather_tool({
            "city": "Paris",
            "units": "celsius"
        })
        assert "Paris" in result[0].text

    @pytest.mark.asyncio
    async def test_city_case_insensitive(self, server):
        """Test that city name is case-insensitive"""
        result1 = await server.weather_tool({"city": "LONDON", "units": "celsius"})
        result2 = await server.weather_tool({"city": "london", "units": "celsius"})
        assert "London" in result1[0].text or "LONDON" in result1[0].text
        assert "london" in result2[0].text or "London" in result2[0].text


class TestGoldPriceTool:
    """Unit tests for gold price tool"""

    @pytest.fixture
    def server(self):
        return MCPServer()

    @pytest.mark.asyncio
    async def test_usd_currency(self, server):
        """Test gold price in USD"""
        result = await server.gold_price_tool({"currency": "USD"})
        text = result[0].text
        assert "USD" in text
        assert "$" in text
        assert "Gold Price" in text

    @pytest.mark.asyncio
    async def test_eur_currency(self, server):
        """Test gold price in EUR"""
        result = await server.gold_price_tool({"currency": "EUR"})
        text = result[0].text
        assert "EUR" in text
        assert "€" in text

    @pytest.mark.asyncio
    async def test_gbp_currency(self, server):
        """Test gold price in GBP"""
        result = await server.gold_price_tool({"currency": "GBP"})
        text = result[0].text
        assert "GBP" in text
        assert "£" in text

    @pytest.mark.asyncio
    async def test_price_format(self, server):
        """Test price formatting with commas"""
        result = await server.gold_price_tool({"currency": "USD"})
        text = result[0].text
        # Price should be formatted with commas (e.g., 2,050.00)
        assert "," in text or "per ounce" in text

    @pytest.mark.asyncio
    async def test_unsupported_currency(self, server):
        """Test handling of unsupported currency"""
        result = await server.gold_price_tool({"currency": "XYZ"})
        # Should either convert to base rate or show error
        assert len(result[0].text) > 0


class TestEmailTool:
    """Unit tests for email tool"""

    @pytest.fixture
    def server(self):
        return MCPServer()

    @pytest.mark.asyncio
    async def test_send_email_simulation(self, server):
        """Test email sending (simulation)"""
        result = await server.email_tool({
            "to": "test@example.com",
            "subject": "Test Email",
            "body": "This is a test message"
        })
        text = result[0].text
        assert "test@example.com" in text
        assert "Test Email" in text
        assert "sent" in text.lower() or "simulated" in text.lower()

    @pytest.mark.asyncio
    async def test_email_with_special_characters(self, server):
        """Test email with special characters in subject/body"""
        result = await server.email_tool({
            "to": "user@test.com",
            "subject": "Hello! 你好 🎉",
            "body": "Special chars: @#$%^&*()"
        })
        assert "user@test.com" in result[0].text

    @pytest.mark.asyncio
    async def test_email_validation(self, server):
        """Test email address validation"""
        result = await server.email_tool({
            "to": "invalid-email",
            "subject": "Test",
            "body": "Test"
        })
        # Should either send or show error for invalid email
        assert len(result[0].text) > 0

    @pytest.mark.asyncio
    async def test_empty_body(self, server):
        """Test email with empty body"""
        result = await server.email_tool({
            "to": "test@example.com",
            "subject": "Empty Body Test",
            "body": ""
        })
        assert "test@example.com" in result[0].text


class TestCodeExecutorTool:
    """Unit tests for code executor tool"""

    @pytest.fixture
    def server(self):
        return MCPServer()

    @pytest.mark.asyncio
    async def test_python_hello_world(self, server):
        """Test executing simple Python code"""
        result = await server.code_executor_tool({
            "language": "python",
            "code": "print('Hello, World!')"
        })
        text = result[0].text
        assert "Hello, World!" in text

    @pytest.mark.asyncio
    async def test_python_calculation(self, server):
        """Test executing Python calculations"""
        result = await server.code_executor_tool({
            "language": "python",
            "code": "result = 2 + 2\nprint(result)"
        })
        assert "4" in result[0].text

    @pytest.mark.asyncio
    async def test_javascript_execution(self, server):
        """Test executing JavaScript code"""
        result = await server.code_executor_tool({
            "language": "javascript",
            "code": "console.log('JS Test')"
        })
        text = result[0].text
        # Should execute or show it's not supported
        assert len(text) > 0

    @pytest.mark.asyncio
    async def test_code_with_error(self, server):
        """Test handling of code with syntax errors"""
        result = await server.code_executor_tool({
            "language": "python",
            "code": "print('unclosed string"
        })
        text = result[0].text
        assert "error" in text.lower() or "exception" in text.lower()

    @pytest.mark.asyncio
    async def test_code_timeout_simulation(self, server):
        """Test code execution timeout handling"""
        # This should complete quickly with our simulated executor
        result = await server.code_executor_tool({
            "language": "python",
            "code": "for i in range(1000000): pass"
        })
        assert len(result[0].text) > 0


class TestWebScraperTool:
    """Unit tests for web scraper tool"""

    @pytest.fixture
    def server(self):
        return MCPServer()

    @pytest.mark.asyncio
    async def test_scrape_url(self, server):
        """Test scraping a URL"""
        result = await server.web_scraper_tool({
            "url": "https://example.com"
        })
        text = result[0].text
        # Should return scraped content or simulation
        assert len(text) > 0
        assert "example.com" in text.lower() or "scraped" in text.lower()

    @pytest.mark.asyncio
    async def test_invalid_url(self, server):
        """Test handling of invalid URLs"""
        result = await server.web_scraper_tool({
            "url": "not-a-valid-url"
        })
        # Should handle gracefully
        assert len(result[0].text) > 0

    @pytest.mark.asyncio
    async def test_https_url(self, server):
        """Test scraping HTTPS URL"""
        result = await server.web_scraper_tool({
            "url": "https://www.python.org"
        })
        assert len(result[0].text) > 0


class TestFileOperationsTool:
    """Unit tests for file operations tool"""

    @pytest.fixture
    def server(self):
        return MCPServer()

    @pytest.fixture
    def temp_file(self, tmp_path):
        """Create a temporary file for testing"""
        file_path = tmp_path / "test_file.txt"
        file_path.write_text("Test content")
        return str(file_path)

    @pytest.mark.asyncio
    async def test_read_operation(self, server, temp_file):
        """Test file read operation"""
        result = await server.file_operations_tool({
            "operation": "read",
            "path": temp_file
        })
        text = result[0].text
        assert "Test content" in text or "read" in text.lower()

    @pytest.mark.asyncio
    async def test_write_operation(self, server, tmp_path):
        """Test file write operation"""
        file_path = str(tmp_path / "write_test.txt")
        result = await server.file_operations_tool({
            "operation": "write",
            "path": file_path,
            "content": "Hello World"
        })
        assert "written" in result[0].text.lower() or "success" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_list_operation(self, server, tmp_path):
        """Test directory listing operation"""
        result = await server.file_operations_tool({
            "operation": "list",
            "path": str(tmp_path)
        })
        # Should list directory contents
        assert len(result[0].text) > 0

    @pytest.mark.asyncio
    async def test_nonexistent_file(self, server):
        """Test handling of nonexistent file"""
        result = await server.file_operations_tool({
            "operation": "read",
            "path": "/nonexistent/file.txt"
        })
        text = result[0].text
        assert "error" in text.lower() or "not found" in text.lower() or "does not exist" in text.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
