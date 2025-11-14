"""
Advanced AI Framework - Enhanced Interactive CLI
Showcases all 31+ tools across 10 domains
"""
import asyncio
import sys
from langchain_mcp_client import LangChainMCPClient


# ANSI color codes for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_header():
    """Print application header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}║                                                                      ║{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}║           🚀 ADVANCED AI FRAMEWORK - Interactive CLI 🚀             ║{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}║                                                                      ║{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}║        LangChain + Ollama + MCP Server + 31+ AI Tools              ║{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}║                                                                      ║{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════╝{Colors.END}\n")

    # Stats
    print(f"{Colors.BOLD}📊 Framework Stats:{Colors.END}")
    print(f"   • {Colors.GREEN}31+{Colors.END} Tools across {Colors.GREEN}10{Colors.END} Domains")
    print(f"   • {Colors.GREEN}6{Colors.END} Specialized AI Agents")
    print(f"   • {Colors.GREEN}100%{Colors.END} Local (No Cloud APIs)")
    print(f"   • {Colors.GREEN}5+{Colors.END} AI Models Integrated\n")


def print_capabilities():
    """Print all available capabilities"""
    capabilities = {
        "📚 RAG System (4 tools)": [
            "rag_index_document - Index any document (PDF, DOCX, code, etc.)",
            "rag_index_directory - Index entire directory",
            "rag_query - Query indexed documents with semantic search",
            "rag_stats - Get RAG system statistics"
        ],
        "💻 Code RAG (3 tools)": [
            "code_analyze_repository - Analyze entire code repository",
            "code_find_function - Find function definitions",
            "code_find_similar - Find similar code patterns"
        ],
        "🎨 Image Generation (2 tools)": [
            "generate_image - Text to image with Stable Diffusion",
            "generate_image_variations - Multiple variations of an image"
        ],
        "⚡ Code Execution (3 tools)": [
            "execute_code - Run Python code safely in sandbox",
            "analyze_code - Analyze code structure without executing",
            "format_code - Format Python code with Black"
        ],
        "🌐 Web Tools (4 tools)": [
            "web_extract_text - Extract readable text from webpages",
            "web_extract_links - Extract all links from a page",
            "web_search_in_page - Search for keywords in webpage",
            "web_download_file - Download files from URLs"
        ],
        "📊 Data Analysis (4 tools)": [
            "data_load_csv - Load CSV/Excel files for analysis",
            "data_get_summary - Get statistical summary",
            "data_query - Query data with pandas syntax",
            "data_create_chart - Create visualizations (bar, line, scatter, etc.)"
        ],
        "📁 File Operations (4 tools)": [
            "file_read - Read file contents",
            "file_write - Write content to files",
            "file_list_directory - List directory contents",
            "file_search - Search for files with patterns"
        ],
        "🔀 Git Operations (3 tools)": [
            "git_status - Get repository status",
            "git_log - View commit history",
            "git_diff - View current changes"
        ],
        "📄 Document Processing (2 tools)": [
            "process_pdf - Extract text from PDFs",
            "summarize_document - Auto-summarize documents"
        ],
        "🔢 Basic Tools (2 tools)": [
            "calculator - Basic arithmetic operations",
            "weather - Get weather information (mock)"
        ]
    }

    print(f"{Colors.BOLD}{Colors.BLUE}╔══════════════════════════════════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}║                        AVAILABLE CAPABILITIES                        ║{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}╚══════════════════════════════════════════════════════════════════════╝{Colors.END}\n")

    for domain, tools in capabilities.items():
        print(f"\n{Colors.BOLD}{Colors.CYAN}{domain}{Colors.END}")
        for tool in tools:
            print(f"  {Colors.GREEN}•{Colors.END} {tool}")

    print(f"\n{Colors.BOLD}🤖 Multi-Agent System:{Colors.END}")
    print(f"  {Colors.GREEN}•{Colors.END} 6 Specialized Agents: Researcher, Coder, Analyst, Writer, Planner, Critic")
    print(f"\n{Colors.BOLD}🧠 Memory & Context:{Colors.END}")
    print(f"  {Colors.GREEN}•{Colors.END} Conversation history and semantic memory\n")


def print_examples():
    """Print example queries"""
    examples = {
        "📚 RAG Examples": [
            "Index all PDFs in ./documents folder",
            "Index the file ./research.pdf",
            "What does the documentation say about installation?",
            "Show me RAG system statistics"
        ],
        "🎨 Image Generation": [
            "Generate an image of a cyberpunk city at sunset",
            "Generate 4 variations of: futuristic robot",
            "Create an image: mountain landscape, oil painting style"
        ],
        "💻 Code Examples": [
            "Execute this code: print([x**2 for x in range(10)])",
            "Analyze this code structure: [paste your code]",
            "Format this Python code: def badly_formatted(x,y):return x+y",
            "Analyze the code repository at ./my_project"
        ],
        "📊 Data Analysis": [
            "Load CSV file ./sales_data.csv as 'sales'",
            "Get summary of dataset 'sales'",
            "Query sales where revenue > 10000",
            "Create bar chart for sales with x='product' y='revenue'"
        ],
        "🌐 Web Scraping": [
            "Extract text from https://example.com/article",
            "Get all links from https://news.ycombinator.com",
            "Search for 'AI' in https://example.com"
        ],
        "📁 File & Git": [
            "List all Python files in current directory",
            "Read the file ./README.md",
            "Show git status",
            "Show last 5 git commits"
        ],
        "🔢 Basic Operations": [
            "What is 25 multiplied by 4?",
            "Calculate 100 divided by 5",
            "What's the weather in Paris?"
        ]
    }

    print(f"{Colors.BOLD}{Colors.YELLOW}╔══════════════════════════════════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.BOLD}{Colors.YELLOW}║                          EXAMPLE QUERIES                             ║{Colors.END}")
    print(f"{Colors.BOLD}{Colors.YELLOW}╚══════════════════════════════════════════════════════════════════════╝{Colors.END}\n")

    for category, queries in examples.items():
        print(f"\n{Colors.BOLD}{Colors.CYAN}{category}:{Colors.END}")
        for i, query in enumerate(queries, 1):
            print(f"  {Colors.GREEN}{i}.{Colors.END} {query}")

    print()


async def interactive_mode():
    """Enhanced interactive mode with all capabilities"""
    print_header()

    print(f"{Colors.BOLD}Welcome to the Advanced AI Framework!{Colors.END}\n")
    print("This system has 31+ tools across 10 domains including:")
    print("  • Document Q&A with RAG")
    print("  • Image generation with Stable Diffusion")
    print("  • Code execution and analysis")
    print("  • Data analysis and visualization")
    print("  • Web scraping and more!\n")

    print(f"{Colors.YELLOW}💡 Tip: Type 'help' to see all capabilities and examples{Colors.END}")
    print(f"{Colors.YELLOW}💡 Tip: Type 'examples' to see example queries{Colors.END}")
    print(f"{Colors.YELLOW}💡 Tip: Type 'quit' or 'exit' to stop{Colors.END}\n")

    # Use advanced server
    client = LangChainMCPClient(model_name="llama3.2")

    # Update the client to use advanced server
    # We'll need to modify the client initialization to use mcp_server_advanced.py

    try:
        print(f"{Colors.CYAN}Initializing AI Framework...{Colors.END}")
        await client.initialize()
        print(f"{Colors.GREEN}✓ System ready!{Colors.END}\n")

        while True:
            try:
                # Get user input with fancy prompt
                query = input(f"{Colors.BOLD}{Colors.BLUE}🤖 You:{Colors.END} ").strip()

                if not query:
                    continue

                # Handle special commands
                if query.lower() in ['quit', 'exit', 'q']:
                    print(f"\n{Colors.CYAN}👋 Thank you for using Advanced AI Framework!{Colors.END}")
                    break

                elif query.lower() == 'help':
                    print_capabilities()
                    continue

                elif query.lower() == 'examples':
                    print_examples()
                    continue

                elif query.lower() == 'clear':
                    print("\033[2J\033[H")  # Clear screen
                    print_header()
                    continue

                # Process the query
                print()  # Blank line before processing
                await client.process_query(query)

            except KeyboardInterrupt:
                print(f"\n\n{Colors.CYAN}👋 Goodbye!{Colors.END}")
                break
            except Exception as e:
                print(f"\n{Colors.RED}❌ Error: {str(e)}{Colors.END}")
                print(f"{Colors.YELLOW}💡 Try 'help' to see available capabilities{Colors.END}\n")

    finally:
        print(f"\n{Colors.CYAN}Cleaning up resources...{Colors.END}")
        await client.cleanup()
        print(f"{Colors.GREEN}✓ Done!{Colors.END}\n")


async def demo_mode():
    """Enhanced demo mode showcasing all capabilities"""
    print_header()

    print(f"{Colors.BOLD}{Colors.GREEN}🎬 DEMO MODE - Showcasing Advanced Capabilities{Colors.END}\n")

    demos = [
        {
            "category": "📚 RAG System",
            "title": "Document Indexing & Q&A",
            "query": "Index the README.md file and tell me what this project does",
            "description": "Demonstrates RAG with document indexing and semantic search"
        },
        {
            "category": "💻 Code Execution",
            "title": "Python Code Sandbox",
            "query": "Execute this code: import math; result = [math.sqrt(x) for x in range(1, 11)]; print(f'Square roots: {result}')",
            "description": "Safe code execution in sandboxed environment"
        },
        {
            "category": "📊 Data Analysis",
            "title": "CSV Analysis",
            "query": "Create a sample dataset with products and sales, then analyze it",
            "description": "Data loading, analysis, and visualization"
        },
        {
            "category": "📁 File Operations",
            "title": "File System Navigation",
            "query": "List all Python files in the current directory",
            "description": "File operations and pattern matching"
        },
        {
            "category": "🔀 Git Operations",
            "title": "Repository Status",
            "query": "Show git status and last 3 commits",
            "description": "Git integration and repository analysis"
        },
        {
            "category": "🔢 Calculator",
            "title": "Math Operations",
            "query": "Calculate 156 multiplied by 23, then add 100",
            "description": "Basic arithmetic with tool chaining"
        }
    ]

    client = LangChainMCPClient(model_name="llama3.2")

    try:
        print(f"{Colors.CYAN}Initializing AI Framework...{Colors.END}")
        await client.initialize()
        print(f"{Colors.GREEN}✓ Ready to demonstrate!{Colors.END}\n")

        for i, demo in enumerate(demos, 1):
            print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
            print(f"{Colors.BOLD}{Colors.CYAN}Demo {i}/{len(demos)}: {demo['category']} - {demo['title']}{Colors.END}")
            print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
            print(f"\n{Colors.YELLOW}Description:{Colors.END} {demo['description']}")
            print(f"{Colors.YELLOW}Query:{Colors.END} {demo['query']}\n")

            input(f"{Colors.GREEN}Press Enter to run this demo...{Colors.END}")
            print()

            await client.process_query(demo['query'])

            if i < len(demos):
                input(f"\n{Colors.CYAN}Press Enter to continue to next demo...{Colors.END}")

        print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}✅ All demos completed!{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.END}\n")

    finally:
        await client.cleanup()


async def capability_explorer():
    """Interactive capability explorer"""
    print_header()

    print(f"{Colors.BOLD}{Colors.CYAN}🔍 CAPABILITY EXPLORER{Colors.END}\n")
    print("Explore each domain with guided examples\n")

    domains = {
        "1": {
            "name": "📚 RAG System",
            "description": "Document intelligence with vector search",
            "examples": [
                "Index the ./README.md file",
                "What is this project about?",
                "Show RAG statistics"
            ]
        },
        "2": {
            "name": "🎨 Image Generation",
            "description": "Local Stable Diffusion image creation",
            "examples": [
                "Generate an image of a sunset over mountains",
                "Generate 3 variations of: a cat in space"
            ]
        },
        "3": {
            "name": "💻 Code Execution",
            "description": "Safe Python code sandbox",
            "examples": [
                "Execute: print([x**2 for x in range(10)])",
                "Analyze this code: def hello(): return 'world'"
            ]
        },
        "4": {
            "name": "📊 Data Analysis",
            "description": "CSV analysis and visualization",
            "examples": [
                "Load a CSV file",
                "Get statistical summary",
                "Create visualizations"
            ]
        },
        "5": {
            "name": "🌐 Web Scraping",
            "description": "Extract content from websites",
            "examples": [
                "Extract text from a URL",
                "Get all links from a page"
            ]
        }
    }

    while True:
        print(f"\n{Colors.BOLD}Select a domain to explore:{Colors.END}")
        for key, domain in domains.items():
            print(f"  {Colors.GREEN}{key}.{Colors.END} {domain['name']} - {domain['description']}")
        print(f"  {Colors.GREEN}0.{Colors.END} Back to main menu\n")

        choice = input(f"{Colors.BLUE}Enter choice (0-5):{Colors.END} ").strip()

        if choice == '0':
            break

        if choice in domains:
            domain = domains[choice]
            print(f"\n{Colors.BOLD}{Colors.CYAN}{domain['name']}{Colors.END}")
            print(f"{domain['description']}\n")
            print(f"{Colors.BOLD}Example queries:{Colors.END}")
            for i, example in enumerate(domain['examples'], 1):
                print(f"  {Colors.GREEN}{i}.{Colors.END} {example}")

            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")
        else:
            print(f"{Colors.RED}Invalid choice!{Colors.END}")


def main():
    """Enhanced main entry point"""
    print_header()

    print(f"{Colors.BOLD}Choose a mode:{Colors.END}\n")
    print(f"  {Colors.GREEN}1.{Colors.END} {Colors.BOLD}Interactive Mode{Colors.END} - Chat with the AI and use all capabilities")
    print(f"  {Colors.GREEN}2.{Colors.END} {Colors.BOLD}Demo Mode{Colors.END} - See guided demonstrations of each domain")
    print(f"  {Colors.GREEN}3.{Colors.END} {Colors.BOLD}Capability Explorer{Colors.END} - Explore domains one by one")
    print(f"  {Colors.GREEN}4.{Colors.END} {Colors.BOLD}Show All Capabilities{Colors.END} - List all 31+ tools")
    print(f"  {Colors.GREEN}5.{Colors.END} {Colors.BOLD}Show Examples{Colors.END} - View example queries")
    print(f"  {Colors.GREEN}0.{Colors.END} {Colors.BOLD}Exit{Colors.END}\n")

    choice = input(f"{Colors.BLUE}Enter your choice (0-5):{Colors.END} ").strip()

    if choice == "1":
        asyncio.run(interactive_mode())
    elif choice == "2":
        asyncio.run(demo_mode())
    elif choice == "3":
        asyncio.run(capability_explorer())
    elif choice == "4":
        print()
        print_capabilities()
        print(f"\n{Colors.YELLOW}Press Enter to return to menu...{Colors.END}")
        input()
        main()
    elif choice == "5":
        print()
        print_examples()
        print(f"\n{Colors.YELLOW}Press Enter to return to menu...{Colors.END}")
        input()
        main()
    elif choice == "0":
        print(f"\n{Colors.CYAN}👋 Thank you for using Advanced AI Framework!{Colors.END}\n")
    else:
        print(f"\n{Colors.RED}Invalid choice. Please try again.{Colors.END}\n")
        main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.CYAN}👋 Goodbye!{Colors.END}\n")
        sys.exit(0)
