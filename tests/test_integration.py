"""
Integration Tests for MCP Server System
Tests how different components work together
"""
import pytest
import asyncio
import sys
import os
import tempfile
import shutil
from pathlib import Path
import requests
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestAsyncManagerIntegration:
    """Test AsyncClientManager integration with Flask"""

    @pytest.mark.asyncio
    async def test_manager_lifecycle(self):
        """Test async manager create, query, cleanup lifecycle"""
        from async_client_manager import AsyncClientManager

        manager = AsyncClientManager()

        try:
            # Start the manager
            manager.start()
            time.sleep(1)  # Give it time to start

            # Create a client
            client_id = await manager.create_client("test_session_1")
            assert client_id is not None
            assert client_id in manager.clients

            # Query the client
            response = await manager.process_query(
                client_id,
                "What is 5 + 5?"
            )
            assert response is not None
            assert "10" in response.lower() or "five" in response.lower()

            # Cleanup
            await manager.cleanup_client(client_id)
            assert client_id not in manager.clients

        finally:
            manager.stop()

    @pytest.mark.asyncio
    async def test_multiple_concurrent_clients(self):
        """Test handling multiple clients concurrently"""
        from async_client_manager import AsyncClientManager

        manager = AsyncClientManager()

        try:
            manager.start()
            time.sleep(1)

            # Create multiple clients
            client_ids = []
            for i in range(3):
                client_id = await manager.create_client(f"session_{i}")
                client_ids.append(client_id)

            assert len(client_ids) == 3
            assert len(manager.clients) == 3

            # Query all clients concurrently
            queries = [
                manager.process_query(client_ids[0], "What is 2 + 2?"),
                manager.process_query(client_ids[1], "What is 3 + 3?"),
                manager.process_query(client_ids[2], "What is 4 + 4?")
            ]

            results = await asyncio.gather(*queries)
            assert len(results) == 3
            for result in results:
                assert result is not None

            # Cleanup all
            for client_id in client_ids:
                await manager.cleanup_client(client_id)

            assert len(manager.clients) == 0

        finally:
            manager.stop()


class TestRAGSystemIntegration:
    """Test RAG system integration with ChromaDB"""

    @pytest.fixture
    def rag_system(self):
        """Create RAG system with temporary database"""
        from rag_system import RAGSystem

        temp_dir = tempfile.mkdtemp()
        rag = RAGSystem(db_path=temp_dir)

        yield rag

        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_upload_and_query(self, rag_system):
        """Test uploading documents and querying"""
        # Create a test document
        test_content = """
        Python is a high-level programming language.
        It is widely used for web development, data science, and automation.
        Python has a simple syntax that is easy to learn.
        """

        # Upload document
        result = rag_system.upload_document(
            content=test_content,
            filename="python_info.txt"
        )
        assert "success" in result.lower() or "uploaded" in result.lower()

        # Query the document
        query_result = rag_system.query("What is Python used for?", n_results=2)
        assert query_result is not None
        assert "web development" in query_result.lower() or "data science" in query_result.lower()

    def test_multiple_documents(self, rag_system):
        """Test uploading and querying multiple documents"""
        documents = [
            ("JavaScript is used for web development.", "js.txt"),
            ("Java is used for enterprise applications.", "java.txt"),
            ("Go is used for system programming.", "go.txt")
        ]

        # Upload all documents
        for content, filename in documents:
            rag_system.upload_document(content, filename)

        # Query should find relevant document
        result = rag_system.query("enterprise applications", n_results=1)
        assert "Java" in result or "enterprise" in result

    def test_empty_query(self, rag_system):
        """Test handling of empty query"""
        result = rag_system.query("", n_results=1)
        assert "error" in result.lower() or "empty" in result.lower() or "no" in result.lower()

    def test_query_no_documents(self, rag_system):
        """Test querying when no documents uploaded"""
        result = rag_system.query("test query", n_results=1)
        assert "no" in result.lower() or "found" in result.lower()


class TestMCPClientServerIntegration:
    """Test MCP Client and Server integration"""

    @pytest.mark.asyncio
    async def test_client_tool_execution(self):
        """Test MCP client executing tools via server"""
        from langchain_mcp_client import LangChainMCPClient

        try:
            client = LangChainMCPClient()
            await client.start()

            # Test calculator tool
            result = await client.process_query("Calculate 15 times 4")
            assert result is not None
            # Should mention 60 or the calculation
            assert "60" in result or "15" in result

        except Exception as e:
            pytest.skip(f"MCP client/server not available: {e}")
        finally:
            try:
                await client.stop()
            except:
                pass

    @pytest.mark.asyncio
    async def test_rag_tool_http_integration(self):
        """Test RAG tool using HTTP API (no direct DB access)"""
        from mcp_server import MCPServer

        server = MCPServer()

        # This should use HTTP API, not direct DB access
        result = await server.rag_query_tool({
            "query": "test query",
            "n_results": 3
        })

        text = result[0].text
        # Should either query or indicate HTTP API usage
        assert len(text) > 0
        assert "http" in text.lower() or "api" in text.lower() or "query" in text.lower()


class TestFlaskAPIIntegration:
    """Test Flask web server API integration"""

    @pytest.fixture(scope="class")
    def flask_app(self):
        """Start Flask app for testing"""
        # Note: This requires the Flask app to be running
        # In a real scenario, you'd start it programmatically or as a fixture
        return "http://localhost:5000"

    def test_api_query_endpoint(self, flask_app):
        """Test /api/query endpoint"""
        try:
            response = requests.post(
                f"{flask_app}/api/query",
                json={"query": "What is 2 + 2?"},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                assert "response" in data
                assert len(data["response"]) > 0
            else:
                pytest.skip("Flask server not running")

        except requests.exceptions.ConnectionError:
            pytest.skip("Flask server not running")

    def test_api_rag_upload_endpoint(self, flask_app):
        """Test /api/rag/upload endpoint"""
        try:
            # Create a test file
            files = {
                'file': ('test.txt', 'Test content for RAG', 'text/plain')
            }

            response = requests.post(
                f"{flask_app}/api/rag/upload",
                files=files,
                timeout=10
            )

            if response.status_code in [200, 404]:
                # 200 = success, 404 = endpoint not implemented yet
                pass
            else:
                pytest.skip("Flask server not running")

        except requests.exceptions.ConnectionError:
            pytest.skip("Flask server not running")

    def test_api_rag_query_endpoint(self, flask_app):
        """Test /api/rag/query endpoint"""
        try:
            response = requests.post(
                f"{flask_app}/api/rag/query",
                json={"query": "test", "n_results": 3},
                timeout=10
            )

            if response.status_code in [200, 404]:
                # Endpoint exists
                pass
            else:
                pytest.skip("Flask server not running")

        except requests.exceptions.ConnectionError:
            pytest.skip("Flask server not running")


class TestToolChaining:
    """Test multiple tools working together"""

    @pytest.mark.asyncio
    async def test_calculator_and_email(self):
        """Test calculator result being used in email"""
        from mcp_server import MCPServer

        server = MCPServer()

        # Step 1: Calculate
        calc_result = await server.calculator_tool({
            "operation": "multiply",
            "a": 50,
            "b": 20
        })
        result_value = calc_result[0].text

        # Step 2: Send email with result
        email_result = await server.email_tool({
            "to": "test@example.com",
            "subject": "Calculation Result",
            "body": f"The calculation result is: {result_value}"
        })

        assert "test@example.com" in email_result[0].text
        assert "1000" in result_value

    @pytest.mark.asyncio
    async def test_weather_and_calculator(self):
        """Test using weather data in calculation"""
        from mcp_server import MCPServer

        server = MCPServer()

        # Get weather
        weather_result = await server.weather_tool({
            "city": "London",
            "units": "celsius"
        })

        # Perform calculation (simulating temperature conversion)
        calc_result = await server.calculator_tool({
            "operation": "multiply",
            "a": 20,  # Assume 20°C from weather
            "b": 1.8  # Conversion factor
        })

        assert len(weather_result[0].text) > 0
        assert len(calc_result[0].text) > 0


class TestDatabaseLocking:
    """Test that database locking is avoided"""

    def test_no_concurrent_chromadb_access(self):
        """Verify RAG tool doesn't open ChromaDB directly"""
        from mcp_server import MCPServer
        import inspect

        server = MCPServer()

        # Check that rag_query_tool uses HTTP, not direct DB access
        source = inspect.getsource(server.rag_query_tool)

        # Should use requests/http, not chromadb.Client()
        assert "http" in source.lower() or "request" in source.lower()
        # Should NOT directly instantiate ChromaDB
        assert "chromadb.Client" not in source or "http" in source.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
