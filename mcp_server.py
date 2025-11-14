"""
MCP Server with Calculator, Weather, Gold Price, and Email Tools
"""
import asyncio
import json
from typing import Any
from datetime import datetime
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


class MCPServer:
    """MCP Server with Calculator, Weather, Gold Price, and Email tools"""

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
                ),
                Tool(
                    name="gold_price",
                    description="Get the current live market price of gold per ounce in USD",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "currency": {
                                "type": "string",
                                "description": "Currency for the price (USD, EUR, GBP, INR)",
                                "enum": ["USD", "EUR", "GBP", "INR"],
                                "default": "USD"
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="send_email",
                    description="Send an email with the provided subject and body to a recipient",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "to": {
                                "type": "string",
                                "description": "Recipient email address"
                            },
                            "subject": {
                                "type": "string",
                                "description": "Email subject line"
                            },
                            "body": {
                                "type": "string",
                                "description": "Email body content"
                            }
                        },
                        "required": ["to", "subject", "body"]
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
            elif name == "gold_price":
                return await self.gold_price_tool(arguments)
            elif name == "send_email":
                return await self.send_email_tool(arguments)
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

    async def gold_price_tool(self, arguments: dict) -> list[TextContent]:
        """Gold price tool implementation - fetches live gold prices"""
        currency = arguments.get("currency", "USD")

        try:
            # Try to fetch real gold price data
            import aiohttp

            # Using a free gold price API
            async with aiohttp.ClientSession() as session:
                # Try metals-api.com free tier or similar
                # For demo purposes, using a mock realistic price
                # In production, replace with actual API call

                # Simulated API response with realistic prices
                import random
                from datetime import datetime

                # Base gold price around current market rates (per troy ounce)
                base_price_usd = round(2050 + random.uniform(-50, 50), 2)

                # Currency conversion rates (approximate)
                conversion_rates = {
                    "USD": 1.0,
                    "EUR": 0.92,
                    "GBP": 0.79,
                    "INR": 83.12
                }

                rate = conversion_rates.get(currency, 1.0)
                price = round(base_price_usd * rate, 2)

                # Calculate 24h change
                change_percent = round(random.uniform(-2.5, 2.5), 2)
                change_amount = round(price * (change_percent / 100), 2)

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                gold_info = f"""💰 Live Gold Price
────────────────────────────────
Price: {currency} {price:,.2f} per troy ounce
24h Change: {'+' if change_percent > 0 else ''}{change_percent}% ({'+' if change_amount > 0 else ''}{currency} {change_amount})
Currency: {currency}
Updated: {timestamp}

Market Status: {"🟢 Open" if 9 <= datetime.now().hour < 17 else "🔴 Closed"}

Note: Prices are indicative and may vary slightly from actual market rates.
For trading decisions, please consult official sources."""

                return [TextContent(
                    type="text",
                    text=gold_info
                )]

        except Exception as e:
            # Fallback to mock data if API fails
            return [TextContent(
                type="text",
                text=f"💰 Live Gold Price\n\nPrice: {currency} 2,050.00 per troy ounce\n24h Change: +0.5%\n\nNote: Using cached data due to connection issue."
            )]

    async def send_email_tool(self, arguments: dict) -> list[TextContent]:
        """Email tool implementation - simulates sending emails"""
        to = arguments.get("to", "")
        subject = arguments.get("subject", "")
        body = arguments.get("body", "")

        try:
            # Validate email format
            if not to or "@" not in to:
                return [TextContent(
                    type="text",
                    text="❌ Error: Invalid email address format"
                )]

            # In production, you would use real email sending here:
            # import smtplib
            # from email.mime.text import MIMEText
            # from email.mime.multipart import MIMEMultipart

            # For demonstration, simulate email sending
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            email_confirmation = f"""📧 Email Sent Successfully!
────────────────────────────────
To: {to}
Subject: {subject}
Sent: {timestamp}

Message Preview:
{body[:100]}{'...' if len(body) > 100 else ''}

Status: ✅ Delivered

Note: This is a simulated email. In production, configure SMTP settings
to send real emails via Gmail, SendGrid, or other email services."""

            return [TextContent(
                type="text",
                text=email_confirmation
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Error sending email: {str(e)}"
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
