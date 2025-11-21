"""
Comprehensive MCP Server Debug Script
Tests all components and identifies issues
"""
import sys
import os
import subprocess
import platform
import asyncio
from datetime import datetime


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")


def test_python_version():
    """Test Python version"""
    print_header("Test 1: Python Version Check")

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    print_info(f"Python Version: {version_str}")
    print_info(f"Platform: {platform.system()} {platform.release()}")
    print_info(f"Architecture: {platform.machine()}")

    if version.major == 3 and 9 <= version.minor <= 12:
        print_success(f"Python {version_str} is compatible")
        return True
    elif version.major == 3 and version.minor == 13:
        print_warning(f"Python {version_str} has known compatibility issues with MCP subprocess")
        print_info("Recommended: Use Python 3.11 or 3.12")
        return "warning"
    else:
        print_error(f"Python {version_str} may not be compatible")
        print_info("Required: Python 3.9-3.12")
        return False


def test_imports():
    """Test if all required modules can be imported"""
    print_header("Test 2: Required Modules")

    modules = [
        ("flask", "Flask web server"),
        ("langchain", "LangChain framework"),
        ("langchain_ollama", "LangChain Ollama integration"),
        ("mcp", "Model Context Protocol"),
        ("chromadb", "Vector database for RAG"),
        ("aiohttp", "Async HTTP client"),
        ("pydantic", "Data validation"),
    ]

    all_ok = True
    for module_name, description in modules:
        try:
            __import__(module_name)
            print_success(f"{module_name:20s} - {description}")
        except ImportError as e:
            print_error(f"{module_name:20s} - Missing! ({description})")
            all_ok = False

    if all_ok:
        print_success("\nAll required modules are installed")
    else:
        print_error("\nSome modules are missing. Run: pip install -r requirements.txt")

    return all_ok


def test_ollama():
    """Test Ollama connection"""
    print_header("Test 3: Ollama Connection")

    try:
        import urllib.request
        import json

        # Test if Ollama is running
        print_info("Testing connection to http://localhost:11434...")
        response = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5)
        data = json.loads(response.read().decode())

        print_success("Ollama is running!")

        if 'models' in data and len(data['models']) > 0:
            print_info(f"Available models ({len(data['models'])}):")
            for model in data['models']:
                print(f"  • {model['name']}")

            # Check for llama3.2
            model_names = [m['name'] for m in data['models']]
            if any('llama3.2' in name for name in model_names):
                print_success("llama3.2 model is available")
                return True
            else:
                print_warning("llama3.2 model not found")
                print_info("Install it with: ollama pull llama3.2")
                return "warning"
        else:
            print_warning("No Ollama models installed")
            print_info("Install a model with: ollama pull llama3.2")
            return "warning"

    except Exception as e:
        print_error(f"Cannot connect to Ollama: {str(e)}")
        print_info("Make sure Ollama is running")
        print_info("Download from: https://ollama.ai/")
        return False


def test_rag_system():
    """Test RAG system initialization"""
    print_header("Test 4: RAG System")

    try:
        from rag_system import get_rag_system

        print_info("Initializing RAG system...")
        rag = get_rag_system()

        # Check if database exists
        stats = rag.get_stats()
        print_success("RAG system initialized successfully")
        print_info(f"Documents in database: {stats['total_documents']}")

        if stats['total_documents'] > 0:
            print_info(f"Total chunks: {stats['total_chunks']}")

        return True

    except Exception as e:
        print_error(f"RAG system failed: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False


def test_mcp_server_import():
    """Test if MCP server can be imported"""
    print_header("Test 5: MCP Server Import")

    try:
        import mcp_server
        print_success("MCP server module imported successfully")
        return True
    except Exception as e:
        print_error(f"Failed to import MCP server: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False


async def test_mcp_server_startup():
    """Test if MCP server can start"""
    print_header("Test 6: MCP Server Startup (Subprocess)")

    try:
        print_info("Attempting to start MCP server as subprocess...")

        # Try to start the server process
        process = await asyncio.create_subprocess_exec(
            sys.executable, "mcp_server.py",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Wait a bit for server to start
        try:
            await asyncio.wait_for(asyncio.sleep(2), timeout=3)
        except:
            pass

        # Check if process is still running
        if process.returncode is None:
            print_success("MCP server started successfully as subprocess")
            process.terminate()
            await process.wait()
            return True
        else:
            stdout, stderr = await process.communicate()
            print_error("MCP server exited immediately")
            if stderr:
                print_info(f"Error output: {stderr.decode()[:200]}")
            return False

    except Exception as e:
        print_error(f"Failed to start MCP server: {str(e)}")
        print_info("This is the Python 3.13 compatibility issue")
        import traceback
        print(traceback.format_exc())
        return False


async def test_mcp_client_connection():
    """Test MCP client connection"""
    print_header("Test 7: MCP Client Connection")

    try:
        from langchain_mcp_client import LangChainMCPClient

        print_info("Creating MCP client...")
        client = LangChainMCPClient(model_name="llama3.2")

        print_info("Attempting to initialize client...")
        await client.initialize()

        print_success("MCP client connected successfully!")

        await client.cleanup()
        return True

    except Exception as e:
        print_error(f"MCP client connection failed: {str(e)}")

        error_str = str(e)
        if "Connection closed" in error_str:
            print_warning("This is the Python 3.13 subprocess communication issue")
            print_info("Solution 1: Use Python 3.11 or 3.12")
            print_info("Solution 2: Use the web interface (python web_server.py)")

        import traceback
        print(traceback.format_exc()[:500])
        return False


def test_web_server_import():
    """Test if web server can be imported"""
    print_header("Test 8: Web Server Import")

    try:
        import web_server
        print_success("Web server module imported successfully")
        return True
    except Exception as e:
        print_error(f"Failed to import web server: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False


def print_summary(results):
    """Print test summary"""
    print_header("Test Summary")

    test_names = [
        "Python Version",
        "Required Modules",
        "Ollama Connection",
        "RAG System",
        "MCP Server Import",
        "MCP Server Startup",
        "MCP Client Connection",
        "Web Server Import"
    ]

    passed = sum(1 for r in results if r is True)
    warnings = sum(1 for r in results if r == "warning")
    failed = sum(1 for r in results if r is False)

    print(f"\n{Colors.BOLD}Results:{Colors.RESET}")
    for name, result in zip(test_names, results):
        if result is True:
            print_success(f"{name:30s} PASSED")
        elif result == "warning":
            print_warning(f"{name:30s} WARNING")
        elif result is False:
            print_error(f"{name:30s} FAILED")

    print(f"\n{Colors.BOLD}Summary:{Colors.RESET}")
    print(f"  Passed:   {Colors.GREEN}{passed}{Colors.RESET}")
    print(f"  Warnings: {Colors.YELLOW}{warnings}{Colors.RESET}")
    print(f"  Failed:   {Colors.RED}{failed}{Colors.RESET}")

    # Provide recommendations
    print_header("Recommendations")

    if results[0] == "warning":  # Python version warning
        print_warning("You're using Python 3.13 which has compatibility issues")
        print_info("Option 1: Install Python 3.11 or 3.12 from https://www.python.org/downloads/")
        print_info("Option 2: Use the web interface: python web_server.py")

    if not results[1]:  # Missing modules
        print_error("Install missing modules:")
        print_info("  pip install -r requirements.txt")

    if not results[2] or results[2] == "warning":  # Ollama issues
        print_warning("Ollama is not properly configured")
        print_info("1. Install Ollama from https://ollama.ai/")
        print_info("2. Run: ollama pull llama3.2")

    if not results[6]:  # MCP client connection failed
        print_warning("MCP client cannot connect (Python 3.13 issue)")
        print_info("RECOMMENDED: Use the web interface instead")
        print_info("  python web_server.py")
        print_info("  Then open http://localhost:5000")

    if results[7]:  # Web server import OK
        print_success("\nGood news: The web server should work!")
        print_info("Try running: python web_server.py")


async def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{'#'*70}{Colors.RESET}")
    print(f"{Colors.BOLD}#{'':^68}#{Colors.RESET}")
    print(f"{Colors.BOLD}#{'MCP Server Comprehensive Diagnostic Tool':^68}#{Colors.RESET}")
    print(f"{Colors.BOLD}#{'':^68}#{Colors.RESET}")
    print(f"{Colors.BOLD}{'#'*70}{Colors.RESET}")
    print(f"\n{Colors.INFO}Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")

    results = []

    # Run synchronous tests
    results.append(test_python_version())
    results.append(test_imports())
    results.append(test_ollama())
    results.append(test_rag_system())
    results.append(test_mcp_server_import())

    # Run async tests
    results.append(await test_mcp_server_startup())
    results.append(await test_mcp_client_connection())
    results.append(test_web_server_import())

    # Print summary
    print_summary(results)

    print(f"\n{Colors.BOLD}Debug complete!{Colors.RESET}\n")


if __name__ == "__main__":
    asyncio.run(main())
