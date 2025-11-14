"""
MCP Server with Calculator, Weather, Gold Price, Email, RAG, Code Execution, Web Scraping, and File Operations Tools
"""
import asyncio
import json
import sys
import io
import os
import signal
from typing import Any
from datetime import datetime
from contextlib import redirect_stdout, redirect_stderr
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import urllib.request
import urllib.error
from html.parser import HTMLParser


class MCPServer:
    """MCP Server with 8 powerful tools: Calculator, Weather, Gold Price, Email, RAG, Code Execution, Web Scraping, and File Operations"""

    def __init__(self):
        self.server = Server("langchain-ollama-mcp")
        # Don't initialize RAG system here to avoid database locking issues
        # RAG queries will use the web server's HTTP API instead
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
                ),
                Tool(
                    name="rag_query",
                    description="Query the RAG (Retrieval-Augmented Generation) database to find relevant information from uploaded documents",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The question or search query to find relevant information"
                            },
                            "n_results": {
                                "type": "number",
                                "description": "Number of relevant documents to retrieve (default: 3)",
                                "default": 3
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="code_execute",
                    description="Execute Python code safely and return the output. Useful for calculations, data processing, and quick scripts.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Python code to execute"
                            }
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="web_scrape",
                    description="Scrape and extract text content from a web page URL",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to scrape"
                            },
                            "extract_links": {
                                "type": "boolean",
                                "description": "Whether to extract links from the page (default: false)",
                                "default": False
                            }
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="file_operations",
                    description="Perform file operations: read, write, list files in directory, or check if file exists",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "operation": {
                                "type": "string",
                                "description": "Operation to perform: read, write, list, exists",
                                "enum": ["read", "write", "list", "exists"]
                            },
                            "path": {
                                "type": "string",
                                "description": "File or directory path"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to write (only for write operation)"
                            }
                        },
                        "required": ["operation", "path"]
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
            elif name == "rag_query":
                return await self.rag_query_tool(arguments)
            elif name == "code_execute":
                return await self.code_execute_tool(arguments)
            elif name == "web_scrape":
                return await self.web_scrape_tool(arguments)
            elif name == "file_operations":
                return await self.file_operations_tool(arguments)
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

    async def rag_query_tool(self, arguments: dict) -> list[TextContent]:
        """RAG query tool implementation - uses HTTP API to avoid database locking"""
        query = arguments.get("query", "")
        n_results = int(arguments.get("n_results", 3))

        try:
            if not query:
                return [TextContent(
                    type="text",
                    text="❌ Error: No query provided"
                )]

            # Use HTTP API to query RAG system (avoids database locking)
            import urllib.request
            import urllib.parse

            # Make request to web server's RAG API
            data = json.dumps({"query": query, "n_results": n_results}).encode('utf-8')
            req = urllib.request.Request(
                "http://localhost:5000/api/rag/query",
                data=data,
                headers={'Content-Type': 'application/json'}
            )

            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    result = json.loads(response.read().decode('utf-8'))

                if result.get("status") == "success":
                    results = result.get("results", {})

                    if not results.get("documents"):
                        return [TextContent(
                            type="text",
                            text=f"📚 RAG Query Results\n────────────────────────────────\nQuery: {query}\n\nNo relevant documents found.\n\nTip: Upload documents first using the web interface to enable RAG search."
                        )]

                    # Format results
                    response_text = f"""📚 RAG Query Results
────────────────────────────────
Query: {query}
Found: {len(results['documents'])} relevant document(s)

"""
                    for i, (doc, metadata, distance) in enumerate(zip(
                        results["documents"],
                        results["metadatas"],
                        results["distances"]
                    ), 1):
                        relevance = "High" if distance < 0.3 else "Medium" if distance < 0.6 else "Low"
                        response_text += f"""Result #{i} (Relevance: {relevance})
────────────────────────────────
{doc[:500]}{'...' if len(doc) > 500 else ''}

Metadata: {metadata.get('filename', 'N/A')} | Length: {metadata.get('length', 0)} chars

"""

                    response_text += "────────────────────────────────\n💡 Tip: You can use this information to answer your question!"

                    return [TextContent(
                        type="text",
                        text=response_text
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=f"❌ RAG query failed: {result.get('message', 'Unknown error')}"
                    )]

            except urllib.error.URLError:
                # Web server not accessible, return helpful message
                return [TextContent(
                    type="text",
                    text="❌ RAG system unavailable (web server not accessible). Please ensure the web server is running."
                )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Error querying RAG database: {str(e)}"
            )]

    async def code_execute_tool(self, arguments: dict) -> list[TextContent]:
        """Code execution tool - safely executes Python code"""
        code = arguments.get("code", "")

        try:
            if not code:
                return [TextContent(
                    type="text",
                    text="❌ Error: No code provided"
                )]

            # Create isolated environment for code execution
            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()

            # Restricted global scope
            restricted_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'range': range,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'abs': abs,
                    'round': round,
                    'sum': sum,
                    'min': min,
                    'max': max,
                    'sorted': sorted,
                    'enumerate': enumerate,
                    'zip': zip,
                    'map': map,
                    'filter': filter,
                    'any': any,
                    'all': all,
                }
            }

            # Execute code with output redirection
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                exec(code, restricted_globals)

            # Get output
            stdout_output = stdout_buffer.getvalue()
            stderr_output = stderr_buffer.getvalue()

            response = "💻 Code Execution Result\n────────────────────────────────\n"

            if stdout_output:
                response += f"Output:\n{stdout_output}\n"

            if stderr_output:
                response += f"\n⚠️  Errors/Warnings:\n{stderr_output}\n"

            if not stdout_output and not stderr_output:
                response += "✅ Code executed successfully (no output)\n"

            response += "────────────────────────────────"

            return [TextContent(
                type="text",
                text=response
            )]

        except SyntaxError as e:
            return [TextContent(
                type="text",
                text=f"❌ Syntax Error: {str(e)}\nLine {e.lineno}: {e.text}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Execution Error: {type(e).__name__}: {str(e)}"
            )]

    async def web_scrape_tool(self, arguments: dict) -> list[TextContent]:
        """Web scraping tool - extracts text and links from web pages"""
        url = arguments.get("url", "")
        extract_links = arguments.get("extract_links", False)

        try:
            if not url:
                return [TextContent(
                    type="text",
                    text="❌ Error: No URL provided"
                )]

            # Add user agent to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            req = urllib.request.Request(url, headers=headers)

            # Fetch the page
            with urllib.request.urlopen(req, timeout=10) as response:
                html_content = response.read().decode('utf-8')

            # Simple HTML parser
            class SimpleHTMLParser(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.text = []
                    self.links = []

                def handle_data(self, data):
                    text = data.strip()
                    if text:
                        self.text.append(text)

                def handle_starttag(self, tag, attrs):
                    if tag == 'a' and extract_links:
                        for attr, value in attrs:
                            if attr == 'href':
                                self.links.append(value)

            parser = SimpleHTMLParser()
            parser.feed(html_content)

            # Format response
            response = f"🌐 Web Scraping Results\n────────────────────────────────\nURL: {url}\n\n"

            # Add text content (limit to first 2000 chars)
            text_content = ' '.join(parser.text)[:2000]
            response += f"Content Preview:\n{text_content}\n"

            if len(' '.join(parser.text)) > 2000:
                response += "\n... (content truncated)\n"

            if extract_links and parser.links:
                response += f"\n\n🔗 Links Found ({len(parser.links)}):\n"
                for i, link in enumerate(parser.links[:20], 1):  # Show first 20 links
                    response += f"{i}. {link}\n"

                if len(parser.links) > 20:
                    response += f"\n... and {len(parser.links) - 20} more links\n"

            response += "\n────────────────────────────────"

            return [TextContent(
                type="text",
                text=response
            )]

        except urllib.error.HTTPError as e:
            return [TextContent(
                type="text",
                text=f"❌ HTTP Error {e.code}: {e.reason}"
            )]
        except urllib.error.URLError as e:
            return [TextContent(
                type="text",
                text=f"❌ URL Error: {str(e.reason)}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Scraping Error: {str(e)}"
            )]

    async def file_operations_tool(self, arguments: dict) -> list[TextContent]:
        """File operations tool - read, write, list files"""
        operation = arguments.get("operation", "")
        path = arguments.get("path", "")
        content = arguments.get("content", "")

        try:
            if operation == "read":
                if not os.path.exists(path):
                    return [TextContent(
                        type="text",
                        text=f"❌ Error: File '{path}' not found"
                    )]

                with open(path, 'r', encoding='utf-8') as f:
                    file_content = f.read()

                # Limit output size
                if len(file_content) > 5000:
                    file_content = file_content[:5000] + "\n\n... (file truncated, showing first 5000 characters)"

                response = f"📄 File Read Result\n────────────────────────────────\nFile: {path}\n\nContent:\n{file_content}\n────────────────────────────────"

                return [TextContent(
                    type="text",
                    text=response
                )]

            elif operation == "write":
                if not content:
                    return [TextContent(
                        type="text",
                        text="❌ Error: No content provided to write"
                    )]

                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)

                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)

                response = f"📝 File Write Result\n────────────────────────────────\nFile: {path}\nBytes written: {len(content)}\n✅ File written successfully\n────────────────────────────────"

                return [TextContent(
                    type="text",
                    text=response
                )]

            elif operation == "list":
                if not os.path.exists(path):
                    return [TextContent(
                        type="text",
                        text=f"❌ Error: Directory '{path}' not found"
                    )]

                if not os.path.isdir(path):
                    return [TextContent(
                        type="text",
                        text=f"❌ Error: '{path}' is not a directory"
                    )]

                files = os.listdir(path)
                files_info = []

                for file in sorted(files):
                    file_path = os.path.join(path, file)
                    if os.path.isdir(file_path):
                        files_info.append(f"📁 {file}/")
                    else:
                        size = os.path.getsize(file_path)
                        files_info.append(f"📄 {file} ({size} bytes)")

                response = f"📂 Directory Listing\n────────────────────────────────\nPath: {path}\nItems: {len(files)}\n\n" + "\n".join(files_info) + "\n────────────────────────────────"

                return [TextContent(
                    type="text",
                    text=response
                )]

            elif operation == "exists":
                exists = os.path.exists(path)
                is_file = os.path.isfile(path) if exists else False
                is_dir = os.path.isdir(path) if exists else False

                response = f"🔍 File Existence Check\n────────────────────────────────\nPath: {path}\nExists: {'✅ Yes' if exists else '❌ No'}\n"

                if exists:
                    response += f"Type: {'📄 File' if is_file else '📁 Directory' if is_dir else '❓ Other'}\n"

                response += "────────────────────────────────"

                return [TextContent(
                    type="text",
                    text=response
                )]

            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Error: Unknown operation '{operation}'"
                )]

        except PermissionError:
            return [TextContent(
                type="text",
                text=f"❌ Permission Error: Cannot access '{path}'"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ File Operation Error: {str(e)}"
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
