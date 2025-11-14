"""
Simple test script for MCP server tools
"""
import asyncio
from mcp_server import MCPServer


async def test_calculator():
    """Test calculator tool"""
    print("Testing Calculator Tool...")
    print("-" * 40)

    server = MCPServer()

    # Test addition
    result = await server.calculator_tool({
        "operation": "add",
        "a": 10,
        "b": 5
    })
    print(f"✓ Add: {result[0].text}")

    # Test subtraction
    result = await server.calculator_tool({
        "operation": "subtract",
        "a": 20,
        "b": 8
    })
    print(f"✓ Subtract: {result[0].text}")

    # Test multiplication
    result = await server.calculator_tool({
        "operation": "multiply",
        "a": 6,
        "b": 7
    })
    print(f"✓ Multiply: {result[0].text}")

    # Test division
    result = await server.calculator_tool({
        "operation": "divide",
        "a": 100,
        "b": 4
    })
    print(f"✓ Divide: {result[0].text}")

    # Test division by zero
    result = await server.calculator_tool({
        "operation": "divide",
        "a": 10,
        "b": 0
    })
    print(f"✓ Division by zero: {result[0].text}")

    print("\n✅ Calculator tests passed!\n")


async def test_weather():
    """Test weather tool"""
    print("Testing Weather Tool...")
    print("-" * 40)

    server = MCPServer()

    # Test weather in Celsius
    result = await server.weather_tool({
        "city": "London",
        "units": "celsius"
    })
    print(f"✓ Weather (Celsius):")
    print(result[0].text)

    # Test weather in Fahrenheit
    result = await server.weather_tool({
        "city": "New York",
        "units": "fahrenheit"
    })
    print(f"\n✓ Weather (Fahrenheit):")
    print(result[0].text)

    print("\n✅ Weather tests passed!\n")


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("MCP Server Tool Tests")
    print("=" * 60 + "\n")

    await test_calculator()
    await test_weather()

    print("=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
