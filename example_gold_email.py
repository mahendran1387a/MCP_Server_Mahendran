"""
Example: Using Gold Price and Email Tools
Demonstrates how to get live gold prices and send emails via MCP
"""
import asyncio
from langchain_mcp_client import LangChainMCPClient


async def example_gold_price():
    """Example: Get live gold price"""
    print("=" * 60)
    print("Example 1: Live Gold Price")
    print("=" * 60)

    client = LangChainMCPClient(model_name="llama3.2")

    try:
        await client.initialize()

        # Get gold price in USD
        print("\n1. Get gold price in USD:")
        await client.process_query("What is the current gold price?")

        # Get gold price in different currency
        print("\n2. Get gold price in EUR:")
        await client.process_query("What is the current gold price in EUR?")

        # Get gold price in INR
        print("\n3. Get gold price in Indian Rupees:")
        await client.process_query("Tell me the live gold price in INR")

    finally:
        await client.cleanup()


async def example_gold_with_email():
    """Example: Get gold price and send it via email"""
    print("\n\n" + "=" * 60)
    print("Example 2: Gold Price + Email")
    print("=" * 60)

    client = LangChainMCPClient(model_name="llama3.2")

    try:
        await client.initialize()

        # Get gold price and email it
        print("\n1. Get gold price and email it:")
        await client.process_query(
            "Get the current gold price in USD and send it to john@example.com with subject 'Daily Gold Price Update'"
        )

    finally:
        await client.cleanup()


async def example_email_only():
    """Example: Send email directly"""
    print("\n\n" + "=" * 60)
    print("Example 3: Send Email")
    print("=" * 60)

    client = LangChainMCPClient(model_name="llama3.2")

    try:
        await client.initialize()

        # Send a simple email
        print("\n1. Send a greeting email:")
        await client.process_query(
            "Send an email to sarah@example.com with subject 'Hello' and body 'Hi Sarah, hope you are doing well!'"
        )

    finally:
        await client.cleanup()


async def example_combined():
    """Example: Use multiple tools together"""
    print("\n\n" + "=" * 60)
    print("Example 4: Combined Tools")
    print("=" * 60)

    client = LangChainMCPClient(model_name="llama3.2")

    try:
        await client.initialize()

        # Use calculator, gold price, and email together
        print("\n1. Multi-tool example:")
        await client.process_query(
            "Calculate 100 times 50, then get the current gold price, and email both results to trader@example.com"
        )

    finally:
        await client.cleanup()


async def main():
    """Run all examples"""
    print("\n" + "#" * 60)
    print("Gold Price & Email Tool Examples")
    print("#" * 60)

    # Run examples
    await example_gold_price()
    await example_gold_with_email()
    await example_email_only()
    await example_combined()

    print("\n\n" + "#" * 60)
    print("All examples completed!")
    print("#" * 60)


if __name__ == "__main__":
    asyncio.run(main())
