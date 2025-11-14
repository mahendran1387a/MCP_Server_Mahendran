"""
Main Application: LangChain + Ollama + MCP Interactive CLI
"""
import asyncio
from langchain_mcp_client import LangChainMCPClient


async def interactive_mode():
    """Run interactive mode where user can ask questions"""
    print("=" * 70)
    print("LangChain + Ollama + MCP Interactive Assistant")
    print("=" * 70)
    print("\nAvailable Tools:")
    print("  • Calculator: Perform arithmetic operations (add, subtract, multiply, divide)")
    print("  • Weather: Get weather information for any city")
    print("\nType 'quit' or 'exit' to stop\n")

    client = LangChainMCPClient(model_name="llama3.2")

    try:
        # Initialize the client
        print("Initializing...")
        await client.initialize()
        print("\nReady! Ask me anything.\n")

        # Interactive loop
        while True:
            try:
                # Get user input
                query = input("\n💬 You: ").strip()

                if not query:
                    continue

                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break

                # Process the query
                await client.process_query(query)

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")

    finally:
        print("\nCleaning up...")
        await client.cleanup()


async def demo_mode():
    """Run demo mode with predefined examples"""
    print("=" * 70)
    print("LangChain + Ollama + MCP Demo Mode")
    print("=" * 70)

    client = LangChainMCPClient(model_name="llama3.2")

    try:
        # Initialize
        await client.initialize()

        # Demo queries
        demos = [
            {
                "title": "Calculator Example",
                "query": "What is 156 multiplied by 23?"
            },
            {
                "title": "Weather Example",
                "query": "What's the weather like in Tokyo?"
            },
            {
                "title": "Multiple Tools Example",
                "query": "Calculate 500 divided by 25, and also tell me the weather in New York."
            },
            {
                "title": "Complex Calculation",
                "query": "Add 100 and 50, then subtract 30 from the result."
            }
        ]

        for i, demo in enumerate(demos, 1):
            print(f"\n\n{'#'*70}")
            print(f"Demo {i}/{len(demos)}: {demo['title']}")
            print(f"{'#'*70}")
            input("\nPress Enter to continue...")

            await client.process_query(demo['query'])

        print("\n\n" + "=" * 70)
        print("Demo completed!")
        print("=" * 70)

    finally:
        await client.cleanup()


def main():
    """Main entry point"""
    import sys

    print("\nLangChain + Ollama + MCP Tools\n")
    print("Choose mode:")
    print("  1. Interactive mode (ask questions)")
    print("  2. Demo mode (see examples)")
    print("  3. Exit\n")

    choice = input("Enter your choice (1-3): ").strip()

    if choice == "1":
        asyncio.run(interactive_mode())
    elif choice == "2":
        asyncio.run(demo_mode())
    elif choice == "3":
        print("Goodbye!")
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)


if __name__ == "__main__":
    main()
