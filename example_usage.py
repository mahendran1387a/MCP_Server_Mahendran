"""
Example Usage: Simple script showing how to use the LangChain + Ollama + MCP client
"""
import asyncio
from langchain_mcp_client import LangChainMCPClient


async def example_calculator():
    """Example: Using the calculator tool"""
    print("=" * 60)
    print("Example 1: Calculator Tool")
    print("=" * 60)

    client = LangChainMCPClient(model_name="llama3.2")

    try:
        await client.initialize()

        # Simple calculation
        print("\n1. Simple calculation:")
        await client.process_query("What is 42 times 13?")

        # Division
        print("\n2. Division:")
        await client.process_query("Divide 144 by 12")

    finally:
        await client.cleanup()


async def example_weather():
    """Example: Using the weather tool"""
    print("\n\n" + "=" * 60)
    print("Example 2: Weather Tool")
    print("=" * 60)

    client = LangChainMCPClient(model_name="llama3.2")

    try:
        await client.initialize()

        # Get weather for a city
        print("\n1. Weather in London:")
        await client.process_query("What's the weather like in London?")

        # Weather with specific units
        print("\n2. Weather in New York (Fahrenheit):")
        await client.process_query("Tell me the weather in New York in Fahrenheit")

    finally:
        await client.cleanup()


async def example_combined():
    """Example: Using multiple tools in one session"""
    print("\n\n" + "=" * 60)
    print("Example 3: Combined Tools")
    print("=" * 60)

    client = LangChainMCPClient(model_name="llama3.2")

    try:
        await client.initialize()

        # Use both tools
        print("\n1. Multiple operations:")
        await client.process_query(
            "Calculate 50 plus 30, and also tell me the weather in Paris"
        )

    finally:
        await client.cleanup()


async def main():
    """Run all examples"""
    print("\n" + "#" * 60)
    print("LangChain + Ollama + MCP - Usage Examples")
    print("#" * 60)

    # Run examples
    await example_calculator()
    await example_weather()
    await example_combined()

    print("\n\n" + "#" * 60)
    print("All examples completed!")
    print("#" * 60)


if __name__ == "__main__":
    asyncio.run(main())
