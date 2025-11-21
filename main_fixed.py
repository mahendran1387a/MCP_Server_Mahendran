"""
Main Application: LangChain + Ollama + MCP Interactive CLI
FIXED VERSION for Python 3.13 - Uses direct mode instead of subprocess
"""
import asyncio
from langchain_mcp_client_fixed import LangChainMCPClientFixed


async def interactive_mode():
    """Run interactive mode where user can ask questions"""
    print("=" * 70)
    print("LangChain + Ollama + MCP Interactive Assistant (FIXED VERSION)")
    print("=" * 70)
    print("\n✅ This version works with Python 3.13!")
    print("✅ Uses DIRECT mode (no subprocess issues)")
    print("\nAvailable Tools:")
    print("  • Calculator: Perform arithmetic operations")
    print("  • Weather: Get weather information")
    print("  • Gold Price: Get current gold prices")
    print("  • Email: Send emails (simulated)")
    print("  • RAG: Query your documents")
    print("\nType 'quit' or 'exit' to stop\n")

    client = LangChainMCPClientFixed(model_name="llama3.2")

    try:
        # Initialize the client
        print("Initializing...")
        await client.initialize()
        print("\n✅ Ready! Ask me anything.\n")

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
    print("LangChain + Ollama + MCP Demo Mode (FIXED VERSION)")
    print("=" * 70)
    print("\n✅ This version works with Python 3.13!")
    print("✅ Uses DIRECT mode (no subprocess issues)\n")

    client = LangChainMCPClientFixed(model_name="llama3.2")

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
                "title": "Gold Price Example",
                "query": "What is the current gold price in USD?"
            },
            {
                "title": "Email Example",
                "query": "Send an email to john@example.com with subject 'Hello' and body 'This is a test'"
            },
            {
                "title": "Multiple Tools Example",
                "query": "Calculate 500 divided by 25, and also tell me the weather in New York."
            },
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

    print("\n🔧 LangChain + Ollama + MCP Tools (FIXED for Python 3.13)")
    print("\nThis version uses DIRECT mode - no subprocess issues!\n")
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
