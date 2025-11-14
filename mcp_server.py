"""
MCP Server with Calculator and Weather Tools
"""
import asyncio
import json
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


class MCPServer:
    """MCP Server with Calculator and Weather tools"""

    def __init__(self):
        self.server = Server("langchain-ollama-mcp")
        self.setup_handlers()

    def setup_handlers(self):
        """Setup request handlers"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="calculator",
                    description="Perform basic arithmetic operations (add, subtract, multiply, divide)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "operation": {
                                "type": "string",
                                "description": "The operation to perform: add, subtract, multiply, or divide",
                                "enum": ["add", "subtract", "multiply", "divide"]
                            },
                            "a": {
                                "type": "number",
                                "description": "First number"
                            },
                            "b": {
                                "type": "number",
                                "description": "Second number"
                            }
                        },
                        "required": ["operation", "a", "b"]
                    }
                ),
                Tool(
                    name="weather",
                    description="Get current weather information for a city (mock data for demonstration)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "The city name to get weather for"
                            },
                            "units": {
                                "type": "string",
                                "description": "Temperature units (celsius or fahrenheit)",
                                "enum": ["celsius", "fahrenheit"],
                                "default": "celsius"
                            }
                        },
                        "required": ["city"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls"""

            if name == "calculator":
                return await self.calculator_tool(arguments)
            elif name == "weather":
                return await self.weather_tool(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def calculator_tool(self, arguments: dict) -> list[TextContent]:
        """Calculator tool implementation"""
        operation = arguments.get("operation")
        a = arguments.get("a")
        b = arguments.get("b")

        try:
            if operation == "add":
                result = a + b
            elif operation == "subtract":
                result = a - b
            elif operation == "multiply":
                result = a * b
            elif operation == "divide":
                if b == 0:
                    return [TextContent(
                        type="text",
                        text="Error: Division by zero"
                    )]
                result = a / b
            else:
                return [TextContent(
                    type="text",
                    text=f"Error: Unknown operation '{operation}'"
                )]

            return [TextContent(
                type="text",
                text=f"Result: {a} {operation} {b} = {result}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]

    async def weather_tool(self, arguments: dict) -> list[TextContent]:
        """Weather tool implementation (mock data)"""
        city = arguments.get("city", "Unknown")
        units = arguments.get("units", "celsius")

        # Mock weather data for demonstration
        import random

        temp_celsius = random.randint(10, 30)
        temp_fahrenheit = (temp_celsius * 9/5) + 32

        conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy", "Overcast"]
        condition = random.choice(conditions)

        humidity = random.randint(30, 80)
        wind_speed = random.randint(5, 25)

        temp = temp_celsius if units == "celsius" else temp_fahrenheit
        temp_unit = "°C" if units == "celsius" else "°F"

        weather_info = f"""Weather in {city}:
Temperature: {temp:.1f}{temp_unit}
Condition: {condition}
Humidity: {humidity}%
Wind Speed: {wind_speed} km/h

Note: This is mock data for demonstration purposes."""

        return [TextContent(
            type="text",
            text=weather_info
        )]

    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point"""
    server = MCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
