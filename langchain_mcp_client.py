"""
LangChain + Ollama Client with MCP Tools Integration
"""
import asyncio
import json
from typing import Any, List
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool


class MCPToolWrapper:
    """Wrapper to convert MCP tools to LangChain tools"""

    def __init__(self, session: ClientSession):
        self.session = session
        self.tools_cache = None

    async def get_tools(self):
        """Get available tools from MCP server"""
        if self.tools_cache is None:
            response = await self.session.list_tools()
            self.tools_cache = response.tools
        return self.tools_cache

    async def call_tool(self, tool_name: str, arguments: dict) -> str:
        """Call an MCP tool"""
        result = await self.session.call_tool(tool_name, arguments)
        # Extract text content from the result
        if result.content:
            return "\n".join(
                item.text for item in result.content if hasattr(item, 'text')
            )
        return "No result"


class LangChainMCPClient:
    """LangChain client that uses Ollama with MCP tools"""

    def __init__(self, model_name: str = "llama3.2"):
        self.model_name = model_name
        self.llm = None
        self.session = None
        self.mcp_wrapper = None
        self.stdio_context = None
        self.read_stream = None
        self.write_stream = None

    async def initialize(self):
        """Initialize the MCP connection and LangChain"""
        # Connect to MCP server
        server_params = StdioServerParameters(
            command="python",
            args=["mcp_server.py"],
            env=None
        )

        # Start MCP client session with proper context manager handling
        self.stdio_context = stdio_client(server_params)
        self.read_stream, self.write_stream = await self.stdio_context.__aenter__()

        # Create the ClientSession with the streams
        self.session = ClientSession(self.read_stream, self.write_stream)
        await self.session.__aenter__()

        # Initialize the session
        await self.session.initialize()

        # Initialize MCP wrapper
        self.mcp_wrapper = MCPToolWrapper(self.session)

        # Initialize Ollama with LangChain
        self.llm = ChatOllama(
            model=self.model_name,
            temperature=0,
        )

        print(f"✓ Initialized LangChain with Ollama model: {self.model_name}")
        print(f"✓ Connected to MCP server")

        # List available tools
        tools = await self.mcp_wrapper.get_tools()
        print(f"✓ Available tools: {', '.join(t.name for t in tools)}")

    async def process_query(self, query: str) -> str:
        """Process a user query using LangChain + Ollama + MCP tools"""
        if not self.llm or not self.mcp_wrapper:
            raise RuntimeError("Client not initialized. Call initialize() first.")

        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")

        # Get available tools
        mcp_tools = await self.mcp_wrapper.get_tools()

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
                    tool_result = await self.mcp_wrapper.call_tool(tool_name, arguments)
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
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
        except Exception as e:
            print(f"Warning: Error cleaning up session: {e}")

        try:
            if self.stdio_context:
                await self.stdio_context.__aexit__(None, None, None)
        except Exception as e:
            print(f"Warning: Error cleaning up stdio context: {e}")


async def main():
    """Main example usage"""
    # Create client
    client = LangChainMCPClient(model_name="llama3.2")

    try:
        # Initialize
        await client.initialize()

        # Example queries
        queries = [
            "What is 25 multiplied by 4?",
            "What's the weather like in Paris?",
            "Calculate 100 divided by 5, and then tell me the weather in London.",
        ]

        for query in queries:
            await client.process_query(query)
            print("\n")

    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
