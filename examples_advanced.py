"""
Advanced Examples - Showcasing All New Capabilities
"""
import asyncio
from langchain_mcp_client import LangChainMCPClient


async def example_rag_system():
    """Example: RAG system for document Q&A"""
    print("\n" + "="*80)
    print("EXAMPLE 1: RAG System - Document Q&A")
    print("="*80)

    client = LangChainMCPClient(model_name="llama3.2")
    await client.initialize()

    queries = [
        # Index documents
        "Index the file ./README.md into the RAG system",

        # Index directory
        "Index all Python files in the current directory for RAG",

        # Query the indexed documents
        "What is this project about based on the indexed documents?",

        # Get statistics
        "Show me the RAG system statistics"
    ]

    for query in queries:
        print(f"\n📝 Query: {query}")
        await client.process_query(query)

    await client.cleanup()


async def example_image_generation():
    """Example: Image generation with Stable Diffusion"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Image Generation")
    print("="*80)

    client = LangChainMCPClient(model_name="llama3.2")
    await client.initialize()

    queries = [
        # Generate single image
        """Generate an image with this prompt:
        'A serene mountain landscape at sunset, oil painting style'
        Use 512x512 resolution with 25 steps""",

        # Generate variations
        "Generate 3 variations of: 'futuristic city with flying cars'"
    ]

    for query in queries:
        print(f"\n🎨 Query: {query}")
        await client.process_query(query)

    await client.cleanup()


async def example_code_execution():
    """Example: Code execution and analysis"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Code Execution & Analysis")
    print("="*80)

    client = LangChainMCPClient(model_name="llama3.2")
    await client.initialize()

    queries = [
        # Execute code
        """Execute this Python code:
        import math
        numbers = [1, 2, 3, 4, 5]
        result = sum([x**2 for x in numbers])
        print(f"Sum of squares: {result}")
        print(f"Square root: {math.sqrt(result)}")
        """,

        # Analyze code
        """Analyze this code structure:
        def fibonacci(n):
            if n <= 1:
                return n
            return fibonacci(n-1) + fibonacci(n-2)

        class DataProcessor:
            def __init__(self):
                self.data = []

            def process(self, item):
                self.data.append(item)
        """,

        # Format code
        """Format this messy code:
        def   badly_formatted( x,y,z ):
            if x>y:return x+z
            else:return y+z
        """
    ]

    for query in queries:
        print(f"\n💻 Query: {query}")
        await client.process_query(query)

    await client.cleanup()


async def example_web_scraping():
    """Example: Web scraping and content extraction"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Web Scraping")
    print("="*80)

    client = LangChainMCPClient(model_name="llama3.2")
    await client.initialize()

    queries = [
        # Extract text
        "Extract readable text from https://example.com",

        # Extract links
        "Get all links from https://news.ycombinator.com",

        # Search in page
        "Search for 'Example' in https://example.com"
    ]

    for query in queries:
        print(f"\n🌐 Query: {query}")
        await client.process_query(query)

    await client.cleanup()


async def example_data_analysis():
    """Example: Data analysis and visualization"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Data Analysis")
    print("="*80)

    # First create sample CSV
    import pandas as pd

    sample_data = {
        'product': ['Laptop', 'Phone', 'Tablet', 'Monitor', 'Keyboard'],
        'category': ['Electronics', 'Electronics', 'Electronics', 'Electronics', 'Accessories'],
        'price': [1200, 800, 500, 300, 50],
        'quantity': [10, 25, 15, 20, 100],
        'revenue': [12000, 20000, 7500, 6000, 5000]
    }

    df = pd.DataFrame(sample_data)
    df.to_csv('./sample_sales.csv', index=False)
    print("✓ Created sample_sales.csv")

    client = LangChainMCPClient(model_name="llama3.2")
    await client.initialize()

    queries = [
        # Load data
        "Load the CSV file ./sample_sales.csv as 'sales'",

        # Get summary
        "Get a statistical summary of the 'sales' dataset",

        # Query data
        "Query the 'sales' dataset where revenue > 8000",

        # Create visualization
        "Create a bar chart for 'sales' with x='product' and y='revenue'"
    ]

    for query in queries:
        print(f"\n📊 Query: {query}")
        await client.process_query(query)

    await client.cleanup()


async def example_file_operations():
    """Example: File system operations"""
    print("\n" + "="*80)
    print("EXAMPLE 6: File Operations")
    print("="*80)

    client = LangChainMCPClient(model_name="llama3.2")
    await client.initialize()

    queries = [
        # List directory
        "List all files in the current directory",

        # Search files
        "Find all Python files in the current directory",

        # Read file
        "Read the contents of ./README.md",

        # Write file
        "Write 'Hello from MCP Server!' to ./test_output.txt"
    ]

    for query in queries:
        print(f"\n📁 Query: {query}")
        await client.process_query(query)

    await client.cleanup()


async def example_git_operations():
    """Example: Git operations"""
    print("\n" + "="*80)
    print("EXAMPLE 7: Git Operations")
    print("="*80)

    client = LangChainMCPClient(model_name="llama3.2")
    await client.initialize()

    queries = [
        # Git status
        "Show the git status of this repository",

        # Git log
        "Show the last 5 git commits",

        # Git diff
        "Show the current git diff"
    ]

    for query in queries:
        print(f"\n🔀 Query: {query}")
        await client.process_query(query)

    await client.cleanup()


async def example_document_processing():
    """Example: Document processing and summarization"""
    print("\n" + "="*80)
    print("EXAMPLE 8: Document Processing")
    print("="*80)

    client = LangChainMCPClient(model_name="llama3.2")
    await client.initialize()

    queries = [
        # Summarize document
        "Summarize the document ./README.md in about 200 characters",

        # Process markdown
        "Extract text from ./HOW_IT_WORKS.md"
    ]

    for query in queries:
        print(f"\n📄 Query: {query}")
        await client.process_query(query)

    await client.cleanup()


async def example_code_rag():
    """Example: Code RAG for repository analysis"""
    print("\n" + "="*80)
    print("EXAMPLE 9: Code RAG - Repository Analysis")
    print("="*80)

    client = LangChainMCPClient(model_name="llama3.2")
    await client.initialize()

    queries = [
        # Analyze repository
        "Analyze and index the code repository at ./ (current directory)",

        # Find function
        "Find the function 'process_query' in the indexed code",

        # Find similar code
        "Find code similar to: async def main():"
    ]

    for query in queries:
        print(f"\n💾 Query: {query}")
        await client.process_query(query)

    await client.cleanup()


async def example_complex_workflow():
    """Example: Complex multi-step workflow"""
    print("\n" + "="*80)
    print("EXAMPLE 10: Complex Multi-Step Workflow")
    print("="*80)

    client = LangChainMCPClient(model_name="llama3.2")
    await client.initialize()

    # Workflow: Analyze project, generate report, create visualization
    queries = [
        "List all Python files in the current directory",
        "Analyze the code structure of ./langchain_mcp_client.py",
        "Summarize the ./README.md file",
        "Show git log for the last 3 commits"
    ]

    print("\n🔄 Running complex workflow...")

    for i, query in enumerate(queries, 1):
        print(f"\n📌 Step {i}/{len(queries)}: {query}")
        await client.process_query(query)

    await client.cleanup()


async def run_all_examples():
    """Run all examples sequentially"""
    examples = [
        ("RAG System", example_rag_system),
        ("Code Execution", example_code_execution),
        ("File Operations", example_file_operations),
        ("Git Operations", example_git_operations),
        ("Document Processing", example_document_processing),
        ("Code RAG", example_code_rag),
        # ("Data Analysis", example_data_analysis),  # Uncomment if you have pandas
        # ("Web Scraping", example_web_scraping),  # Uncomment if you have internet
        # ("Image Generation", example_image_generation),  # Uncomment if you have GPU/time
    ]

    print("\n" + "🚀 RUNNING ALL EXAMPLES" + "\n")

    for name, example_func in examples:
        try:
            print(f"\n{'='*80}")
            print(f"Starting: {name}")
            print(f"{'='*80}")
            await example_func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {str(e)}")
            continue

    print("\n" + "="*80)
    print("✅ ALL EXAMPLES COMPLETED!")
    print("="*80)


def main():
    """Main entry point"""
    import sys

    print("\n🎯 Advanced Examples - MCP Server Framework\n")
    print("Choose an example to run:")
    print("  1.  RAG System")
    print("  2.  Image Generation")
    print("  3.  Code Execution")
    print("  4.  Web Scraping")
    print("  5.  Data Analysis")
    print("  6.  File Operations")
    print("  7.  Git Operations")
    print("  8.  Document Processing")
    print("  9.  Code RAG")
    print("  10. Complex Workflow")
    print("  11. Run All Examples")
    print("  0.  Exit")

    choice = input("\nEnter your choice (0-11): ").strip()

    examples = {
        "1": example_rag_system,
        "2": example_image_generation,
        "3": example_code_execution,
        "4": example_web_scraping,
        "5": example_data_analysis,
        "6": example_file_operations,
        "7": example_git_operations,
        "8": example_document_processing,
        "9": example_code_rag,
        "10": example_complex_workflow,
        "11": run_all_examples,
    }

    if choice == "0":
        print("Goodbye!")
        sys.exit(0)

    if choice in examples:
        asyncio.run(examples[choice]())
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)


if __name__ == "__main__":
    main()
