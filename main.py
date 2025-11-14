"""
Advanced AI Framework - Main Application
LangChain + Ollama + MCP Server with 31+ Tools
"""
import asyncio
import sys
from langchain_mcp_client import LangChainMCPClient


def print_banner():
    """Print application banner"""
    print("\n" + "="*80)
    print("           🚀 ADVANCED AI FRAMEWORK - Interactive Assistant 🚀")
    print("="*80)
    print("\n📊 System Capabilities:")
    print("   • 31+ AI Tools across 10 domains")
    print("   • RAG for document Q&A")
    print("   • Image generation with Stable Diffusion")
    print("   • Code execution and analysis")
    print("   • Data analysis and visualization")
    print("   • Web scraping and content extraction")
    print("   • File operations and Git integration")
    print("   • Multi-agent orchestration")
    print("   • 100% Local (No cloud APIs)\n")


def print_quick_help():
    """Print quick help guide"""
    print("💡 Quick Start Examples:")
    print("   📚 RAG: 'Index ./README.md and tell me what this project does'")
    print("   🎨 Image: 'Generate an image of a cyberpunk city'")
    print("   💻 Code: 'Execute: print([x**2 for x in range(10)])'")
    print("   📊 Data: 'Load CSV file ./data.csv and analyze it'")
    print("   🌐 Web: 'Extract text from https://example.com'")
    print("   📁 Files: 'List all Python files in current directory'")
    print("   🔀 Git: 'Show git status and last 3 commits'")
    print("   🔢 Math: 'Calculate 25 times 4'\n")
    print("💡 Commands:")
    print("   'help' - Show all capabilities")
    print("   'examples' - Show more example queries")
    print("   'quit' or 'exit' - Exit the application\n")


async def interactive_mode():
    """Run interactive mode where user can use all capabilities"""
    print_banner()
    print_quick_help()

    client = LangChainMCPClient(model_name="llama3.2")

    try:
        # Initialize with advanced server
        print("🔄 Initializing AI Framework...")
        await client.initialize(use_advanced_server=True)
        print("✅ System ready! All 31+ tools loaded.\n")

        # Interactive loop
        while True:
            try:
                # Get user input
                query = input("💬 You: ").strip()

                if not query:
                    continue

                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break

                if query.lower() == 'help':
                    print_capabilities()
                    continue

                if query.lower() == 'examples':
                    print_examples()
                    continue

                # Process the query with all tools available
                print()
                await client.process_query(query)

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("💡 Try 'help' to see available capabilities\n")

    finally:
        print("\n🔄 Cleaning up...")
        await client.cleanup()


def print_capabilities():
    """Print all available capabilities"""
    print("\n" + "="*80)
    print("                         AVAILABLE CAPABILITIES")
    print("="*80 + "\n")

    capabilities = [
        ("📚 RAG System (4 tools)", [
            "Index documents (PDF, DOCX, code, etc.)",
            "Semantic search with vector embeddings",
            "Query indexed knowledge base",
            "Get system statistics"
        ]),
        ("🎨 Image Generation (2 tools)", [
            "Text-to-image with Stable Diffusion",
            "Generate multiple variations"
        ]),
        ("💻 Code Tools (6 tools)", [
            "Execute Python code safely",
            "Analyze code structure",
            "Format code with Black",
            "Analyze repositories",
            "Find functions and patterns"
        ]),
        ("📊 Data Analysis (4 tools)", [
            "Load CSV/Excel files",
            "Statistical analysis",
            "Query data with pandas",
            "Create visualizations"
        ]),
        ("🌐 Web Tools (4 tools)", [
            "Extract webpage text",
            "Get all links",
            "Search in pages",
            "Download files"
        ]),
        ("📁 File & Git (7 tools)", [
            "Read/write files",
            "List directories",
            "Search files",
            "Git status/log/diff"
        ]),
        ("📄 Documents (2 tools)", [
            "Process PDFs",
            "Summarize documents"
        ]),
        ("🤖 Advanced Features", [
            "Multi-agent orchestration (6 agents)",
            "Conversation memory",
            "Context management"
        ])
    ]

    for category, items in capabilities:
        print(f"{category}")
        for item in items:
            print(f"  • {item}")
        print()


def print_examples():
    """Print example queries"""
    print("\n" + "="*80)
    print("                           EXAMPLE QUERIES")
    print("="*80 + "\n")

    examples = [
        ("📚 Document Intelligence", [
            "Index all PDF files in ./documents",
            "What are the key points in the indexed documents?",
            "Summarize ./report.pdf"
        ]),
        ("🎨 Creative Content", [
            "Generate an image: sunset over mountains, oil painting",
            "Create 4 variations of: futuristic robot"
        ]),
        ("💻 Code Operations", [
            "Execute: import math; print(math.pi ** 2)",
            "Analyze code repository at ./my_project",
            "Find function 'process_data' in indexed code"
        ]),
        ("📊 Data Science", [
            "Load ./sales.csv as 'sales' and show summary",
            "Query sales where revenue > 10000",
            "Create bar chart for sales by product"
        ]),
        ("🌐 Web Research", [
            "Extract article from https://example.com/blog",
            "Get all links from https://news.ycombinator.com"
        ]),
        ("📁 Development", [
            "List all Python files recursively",
            "Show git status",
            "Read ./config.json"
        ])
    ]

    for category, queries in examples:
        print(f"{category}")
        for i, query in enumerate(queries, 1):
            print(f"  {i}. {query}")
        print()


async def demo_mode():
    """Run demo mode with predefined examples showcasing new capabilities"""
    print_banner()
    print("🎬 DEMO MODE - Showcasing Advanced Capabilities\n")

    client = LangChainMCPClient(model_name="llama3.2")

    try:
        # Initialize with advanced server
        print("🔄 Initializing...")
        await client.initialize(use_advanced_server=True)
        print("✅ Ready!\n")

        # Demo queries showcasing different capabilities
        demos = [
            {
                "title": "💻 Code Execution",
                "query": "Execute this Python code: result = [x**2 for x in range(1, 6)]; print(f'Squares: {result}')"
            },
            {
                "title": "📁 File Operations",
                "query": "List all Python files in the current directory"
            },
            {
                "title": "🔀 Git Integration",
                "query": "Show git status"
            },
            {
                "title": "📚 Document Processing",
                "query": "Read the README.md file and tell me what this project does"
            },
            {
                "title": "🔢 Calculator",
                "query": "What is 156 multiplied by 23?"
            }
        ]

        for i, demo in enumerate(demos, 1):
            print(f"\n{'='*80}")
            print(f"Demo {i}/{len(demos)}: {demo['title']}")
            print(f"{'='*80}")
            print(f"Query: {demo['query']}\n")

            input("Press Enter to run this demo...")
            print()

            await client.process_query(demo['query'])

            if i < len(demos):
                input("\nPress Enter to continue to next demo...")

        print(f"\n{'='*80}")
        print("✅ All demos completed!")
        print(f"{'='*80}\n")

    finally:
        await client.cleanup()


def main():
    """Main entry point"""
    print_banner()

    print("Choose mode:\n")
    print("  1. Interactive mode (chat with AI)")
    print("  2. Demo mode (see examples)")
    print("  3. Show all capabilities")
    print("  4. Exit\n")

    choice = input("Enter your choice (1-4): ").strip()

    if choice == "1":
        asyncio.run(interactive_mode())
    elif choice == "2":
        asyncio.run(demo_mode())
    elif choice == "3":
        print_capabilities()
        print("\nPress Enter to return to menu...")
        input()
        main()
    elif choice == "4":
        print("\n👋 Goodbye!")
    else:
        print("\n❌ Invalid choice. Please try again.\n")
        main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
