"""
LangChain + Ollama Client with MCP Tools Integration
FIXED VERSION for Python 3.13 compatibility
"""
import asyncio
import json
import sys
from typing import Any, List
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage


class DirectMCPServer:
    """
    Direct MCP server integration without subprocess
    Works around Python 3.13 subprocess issues
    """

    def __init__(self):
        # Import here to avoid circular imports
        from rag_system import get_rag_system
        self.rag_system = get_rag_system()

    async def list_tools(self):
        """List available tools"""
        from datetime import datetime
        import random

        class Tool:
            def __init__(self, name, description, inputSchema):
                self.name = name
                self.description = description
                self.inputSchema = inputSchema

        tools = [
            Tool(
                name="calculator",
                description="Perform basic arithmetic operations (add, subtract, multiply, divide)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "description": "The operation to perform",
                            "enum": ["add", "subtract", "multiply", "divide"]
                        },
                        "a": {"type": "number", "description": "First number"},
                        "b": {"type": "number", "description": "Second number"}
                    },
                    "required": ["operation", "a", "b"]
                }
            ),
            Tool(
                name="weather",
                description="Get weather information for any city",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "city": {"type": "string", "description": "City name"},
                        "units": {
                            "type": "string",
                            "description": "Temperature units",
                            "enum": ["celsius", "fahrenheit"]
                        }
                    },
                    "required": ["city"]
                }
            ),
            Tool(
                name="gold_price",
                description="Get current gold price in different currencies",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "currency": {
                            "type": "string",
                            "description": "Currency code",
                            "enum": ["USD", "EUR", "GBP", "INR"]
                        }
                    }
                }
            ),
            Tool(
                name="send_email",
                description="Send an email (simulated)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email"},
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body"}
                    },
                    "required": ["to", "subject", "body"]
                }
            ),
            Tool(
                name="rag_query",
                description="Query uploaded documents using RAG",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "n_results": {"type": "number", "description": "Number of results"}
                    },
                    "required": ["query"]
                }
            ),
        ]

        return tools

    async def call_tool(self, tool_name: str, arguments: dict) -> str:
        """Call a tool directly"""
        try:
            if tool_name == "calculator":
                return await self._calculator(arguments)
            elif tool_name == "weather":
                return await self._weather(arguments)
            elif tool_name == "gold_price":
                return await self._gold_price(arguments)
            elif tool_name == "send_email":
                return await self._send_email(arguments)
            elif tool_name == "rag_query":
                return await self._rag_query(arguments)
            else:
                return f"Unknown tool: {tool_name}"
        except Exception as e:
            return f"Error calling tool {tool_name}: {str(e)}"

    async def _calculator(self, args: dict) -> str:
        """Calculator tool implementation"""
        operation = args.get("operation")
        a = float(args.get("a", 0))
        b = float(args.get("b", 0))

        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                return "❌ Error: Division by zero"
            result = a / b
        else:
            return f"❌ Unknown operation: {operation}"

        return f"🧮 Calculator Result\n────────────────────────────────\n{a} {operation} {b} = {result}\n────────────────────────────────"

    async def _weather(self, args: dict) -> str:
        """Weather tool implementation (mock data)"""
        import random
        from datetime import datetime

        city = args.get("city", "Unknown")
        units = args.get("units", "celsius")

        # Mock weather data
        temp_c = random.randint(15, 30)
        temp_f = int(temp_c * 9/5 + 32)
        conditions = random.choice(["Sunny", "Cloudy", "Partly Cloudy", "Rainy"])
        humidity = random.randint(40, 80)

        temp = temp_c if units == "celsius" else temp_f
        unit_symbol = "°C" if units == "celsius" else "°F"

        return f"""🌤️ Weather in {city}
────────────────────────────────
Temperature: {temp}{unit_symbol}
Condition: {conditions}
Humidity: {humidity}%
Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
────────────────────────────────"""

    async def _gold_price(self, args: dict) -> str:
        """Gold price tool implementation (mock data)"""
        import random
        from datetime import datetime

        currency = args.get("currency", "USD")

        # Base price in USD (mock)
        base_price = 2050 + random.uniform(-50, 50)

        # Currency conversion (mock rates)
        rates = {"USD": 1.0, "EUR": 0.92, "GBP": 0.79, "INR": 83.12}
        rate = rates.get(currency, 1.0)
        price = base_price * rate

        change = random.uniform(-2, 2)
        change_symbol = "+" if change > 0 else ""

        return f"""💰 Live Gold Price
────────────────────────────────
Price: {currency} {price:.2f} per troy ounce
24h Change: {change_symbol}{change:.2f}%
Currency: {currency}
Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Market Status: 🟢 Open
────────────────────────────────"""

    async def _send_email(self, args: dict) -> str:
        """Email tool implementation (simulated)"""
        from datetime import datetime

        to = args.get("to", "")
        subject = args.get("subject", "")
        body = args.get("body", "")

        return f"""📧 Email Sent Successfully!
────────────────────────────────
To: {to}
Subject: {subject}
Sent: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Message Preview:
{body[:100]}{'...' if len(body) > 100 else ''}

Status: ✅ Delivered
────────────────────────────────"""

    async def _rag_query(self, args: dict) -> str:
        """RAG query tool implementation"""
        query = args.get("query", "")
        n_results = int(args.get("n_results", 3))

        if not query:
            return "❌ Error: No query provided"

        try:
            results = self.rag_system.query(query, n_results=n_results)

            if not results or len(results['documents'][0]) == 0:
                return f"""📚 RAG Query Results
────────────────────────────────
Query: {query}
Found: 0 documents

No relevant documents found. Try:
1. Uploading documents via web interface
2. Using different search terms
────────────────────────────────"""

            output = f"""📚 RAG Query Results
────────────────────────────────
Query: {query}
Found: {len(results['documents'][0])} relevant document(s)
"""

            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            ), 1):
                relevance = "High" if distance < 0.5 else "Medium" if distance < 1.0 else "Low"
                output += f"""
Result #{i} (Relevance: {relevance})
────────────────────────────────
{doc[:300]}{'...' if len(doc) > 300 else ''}

Source: {metadata.get('source', 'Unknown')}
────────────────────────────────"""

            return output

        except Exception as e:
            return f"❌ RAG Query Error: {str(e)}"


class LangChainMCPClientFixed:
    """
    LangChain client with direct MCP integration (no subprocess)
    This version works with Python 3.13
    """

    def __init__(self, model_name: str = "llama3.2", use_direct_mode: bool = True):
        self.model_name = model_name
        self.llm = None
        self.mcp_server = None
        self.use_direct_mode = use_direct_mode

    async def initialize(self):
        """Initialize the client with direct MCP server"""
        print(f"✓ Using DIRECT mode (Python 3.13 compatible)")

        # Initialize direct MCP server
        self.mcp_server = DirectMCPServer()

        # Initialize Ollama with LangChain
        self.llm = ChatOllama(
            model=self.model_name,
            temperature=0,
        )

        print(f"✓ Initialized LangChain with Ollama model: {self.model_name}")

        # List available tools
        tools = await self.mcp_server.list_tools()
        print(f"✓ Available tools: {', '.join(t.name for t in tools)}")

    async def process_query(self, query: str) -> str:
        """Process a user query using LangChain + Ollama + MCP tools"""
        if not self.llm or not self.mcp_server:
            raise RuntimeError("Client not initialized. Call initialize() first.")

        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")

        # Get available tools
        mcp_tools = await self.mcp_server.list_tools()

        # Create a system prompt that includes tool information
        tools_description = self._format_tools_description(mcp_tools)

        system_prompt = f"""You are a helpful assistant with access to the following tools:

{tools_description}

When you need to use a tool, respond with a JSON object in this format:
{{"tool": "tool_name", "arguments": {{"arg1": "value1", "arg2": "value2"}}}}

If you don't need to use a tool, just respond normally.

Important: Only use the tools when necessary to answer the user's question."""

        # Initial query to the LLM
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]

        max_iterations = 5
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Get response from Ollama
            response = self.llm.invoke(messages)
            response_text = response.content

            print(f"\nLLM Response (iteration {iteration}):")
            print(response_text)

            # Check if the response contains a tool call
            tool_call = self._extract_tool_call(response_text)

            if tool_call:
                tool_name = tool_call.get("tool")
                arguments = tool_call.get("arguments", {})

                print(f"\n🔧 Calling tool: {tool_name}")
                print(f"   Arguments: {json.dumps(arguments, indent=2)}")

                # Call the MCP tool
                try:
                    tool_result = await self.mcp_server.call_tool(tool_name, arguments)
                    print(f"\n📊 Tool Result:")
                    print(tool_result)

                    # Add the tool result to the conversation
                    messages.append({"role": "assistant", "content": response_text})
                    messages.append({
                        "role": "user",
                        "content": f"Tool '{tool_name}' returned: {tool_result}\n\nPlease provide a natural language response to the user based on this result."
                    })
                except Exception as e:
                    error_msg = f"Error calling tool: {str(e)}"
                    print(f"\n❌ {error_msg}")
                    messages.append({"role": "assistant", "content": response_text})
                    messages.append({
                        "role": "user",
                        "content": f"Tool call failed: {error_msg}\n\nPlease respond to the user explaining the error."
                    })
            else:
                # No tool call detected, return the response
                print(f"\n{'='*60}")
                print(f"Final Answer:")
                print(response_text)
                print(f"{'='*60}")
                return response_text

        return "Maximum iterations reached. Could not complete the request."

    def _format_tools_description(self, tools) -> str:
        """Format tools for the system prompt"""
        descriptions = []
        for tool in tools:
            desc = f"- {tool.name}: {tool.description}"
            if tool.inputSchema:
                desc += f"\n  Parameters: {json.dumps(tool.inputSchema.get('properties', {}), indent=2)}"
            descriptions.append(desc)
        return "\n\n".join(descriptions)

    def _extract_tool_call(self, text: str) -> dict | None:
        """Extract tool call from LLM response"""
        # Try to find JSON in the response
        try:
            # Look for JSON object in the text
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end > start:
                json_str = text[start:end]
                data = json.loads(json_str)
                if "tool" in data:
                    return data
        except json.JSONDecodeError:
            pass
        return None

    async def cleanup(self):
        """Cleanup resources"""
        print("Cleanup complete")


async def main():
    """Main example usage"""
    # Create client with fixed version
    client = LangChainMCPClientFixed(model_name="llama3.2")

    try:
        # Initialize
        await client.initialize()

        # Example queries
        queries = [
            "What is 25 multiplied by 4?",
            "What's the weather like in Paris?",
            "What is the current gold price in USD?",
        ]

        for query in queries:
            await client.process_query(query)
            print("\n")

    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
