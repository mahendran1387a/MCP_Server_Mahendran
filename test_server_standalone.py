"""
Test script to diagnose MCP server startup issues
"""
import sys
import subprocess

def test_server_import():
    """Test if the server can be imported"""
    print("=" * 60)
    print("Test 1: Testing server import...")
    print("=" * 60)
    try:
        import mcp_server
        print("✅ Server imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_server_startup():
    """Test if the server can start"""
    print("\n" + "=" * 60)
    print("Test 2: Testing server startup...")
    print("=" * 60)
    try:
        # Try to run the server with a timeout
        result = subprocess.run(
            [sys.executable, "mcp_server.py"],
            capture_output=True,
            text=True,
            timeout=2
        )
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"STDERR:\n{result.stderr}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⚠️  Server is running but didn't exit (this is expected)")
        return True
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rag_system():
    """Test if RAG system can be initialized"""
    print("\n" + "=" * 60)
    print("Test 3: Testing RAG system...")
    print("=" * 60)
    try:
        from rag_system import get_rag_system
        rag = get_rag_system()
        print("✅ RAG system initialized successfully")
        return True
    except Exception as e:
        print(f"❌ RAG system failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🔍 MCP Server Diagnostic Tool\n")

    results = {
        "Import Test": test_server_import(),
        "RAG System Test": test_rag_system(),
        "Server Startup Test": test_server_startup(),
    }

    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")

    all_passed = all(results.values())
    if all_passed:
        print("\n✅ All tests passed! The server should work correctly.")
    else:
        print("\n❌ Some tests failed. Please review the errors above.")
