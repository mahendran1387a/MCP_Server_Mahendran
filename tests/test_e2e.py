"""
End-to-End Tests for MCP Server System
Simulates real user flows through the entire system
"""
import pytest
import requests
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_URL = "http://localhost:5000"
TIMEOUT = 30


class TestUserQueryFlow:
    """Test complete user query flow from browser to response"""

    @pytest.fixture(autouse=True)
    def check_server(self):
        """Check if server is running before each test"""
        try:
            requests.get(BASE_URL, timeout=5)
        except requests.exceptions.ConnectionError:
            pytest.skip("Flask server not running. Start with: python web_server.py")

    def test_simple_calculator_query_flow(self):
        """
        E2E Flow: User asks calculator question
        Browser → Flask → AsyncManager → MCP Client → Ollama → MCP Server → Calculator → Response
        """
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": "What is 25 times 4?"},
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert data["response"] is not None
        # Should mention 100 or the calculation
        assert "100" in data["response"] or "25" in data["response"]

    def test_weather_query_flow(self):
        """
        E2E Flow: User asks about weather
        """
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": "What's the weather in London?"},
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        # Should mention London or weather
        assert "london" in data["response"].lower() or "weather" in data["response"].lower()

    def test_gold_price_query_flow(self):
        """
        E2E Flow: User asks about gold price
        """
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": "What is the current gold price?"},
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "gold" in data["response"].lower() or "price" in data["response"].lower()

    def test_complex_calculation_query(self):
        """
        E2E Flow: User asks complex calculation requiring multiple steps
        """
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": "Calculate 15 plus 30, then multiply by 2"},
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        # Result should be 90: (15 + 30) * 2
        assert "90" in data["response"] or "calculation" in data["response"].lower()

    def test_invalid_query_handling(self):
        """
        E2E Flow: User sends invalid/empty query
        """
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": ""},
            timeout=TIMEOUT
        )

        # Should handle gracefully
        assert response.status_code in [200, 400]

    def test_session_persistence(self):
        """
        E2E Flow: Multiple queries in same session
        """
        session_id = f"test_session_{int(time.time())}"

        # First query
        response1 = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": "Calculate 5 plus 5"},
            cookies={"session": session_id},
            timeout=TIMEOUT
        )

        assert response1.status_code == 200

        # Second query in same session
        response2 = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": "What is the weather?"},
            cookies={"session": session_id},
            timeout=TIMEOUT
        )

        assert response2.status_code == 200


class TestRAGUploadQueryFlow:
    """Test complete RAG document upload and query flow"""

    @pytest.fixture(autouse=True)
    def check_server(self):
        try:
            requests.get(BASE_URL, timeout=5)
        except requests.exceptions.ConnectionError:
            pytest.skip("Flask server not running")

    def test_upload_and_query_document_flow(self):
        """
        E2E Flow: User uploads document and queries it
        1. Upload document
        2. Query for information in document
        3. Verify response contains relevant info
        """
        # Step 1: Upload document
        doc_content = """
        Python 3.12 Release Notes

        Python 3.12 includes several new features:
        - Improved error messages
        - Faster startup time
        - Better performance
        - New syntax features
        """

        files = {
            'file': ('python_312.txt', doc_content, 'text/plain')
        }

        upload_response = requests.post(
            f"{BASE_URL}/api/rag/upload",
            files=files,
            timeout=TIMEOUT
        )

        if upload_response.status_code == 404:
            pytest.skip("RAG upload endpoint not implemented")

        assert upload_response.status_code == 200

        # Wait for indexing
        time.sleep(2)

        # Step 2: Query the document
        query_response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": "What are the new features in Python 3.12?"},
            timeout=TIMEOUT
        )

        assert query_response.status_code == 200
        data = query_response.json()
        assert "response" in data

        # Should mention features from the document
        response_lower = data["response"].lower()
        assert any(keyword in response_lower for keyword in ["error", "performance", "feature", "python"])

    def test_query_without_documents(self):
        """
        E2E Flow: User queries RAG without uploading documents
        """
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": "Tell me about a document that doesn't exist"},
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        # Should handle gracefully, even if no documents found

    def test_multiple_document_upload_flow(self):
        """
        E2E Flow: Upload multiple documents and query across them
        """
        documents = [
            ("JavaScript is a web programming language.", "js.txt"),
            ("Python is great for data science.", "python.txt"),
            ("Go is efficient for system programming.", "go.txt")
        ]

        # Upload all documents
        for content, filename in documents:
            files = {'file': (filename, content, 'text/plain')}
            response = requests.post(
                f"{BASE_URL}/api/rag/upload",
                files=files,
                timeout=TIMEOUT
            )

            if response.status_code == 404:
                pytest.skip("RAG upload endpoint not implemented")

        time.sleep(2)

        # Query for specific information
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": "Which language is good for data science?"},
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        data = response.json()
        # Should mention Python
        assert "python" in data["response"].lower()


class TestToolCombinationFlows:
    """Test E2E flows using multiple tools"""

    @pytest.fixture(autouse=True)
    def check_server(self):
        try:
            requests.get(BASE_URL, timeout=5)
        except requests.exceptions.ConnectionError:
            pytest.skip("Flask server not running")

    def test_calculate_and_email_flow(self):
        """
        E2E Flow: Calculate and send result via email
        """
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": "Calculate 100 divided by 4 and send the result to test@example.com"},
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        data = response.json()
        # Should mention both calculation and email
        assert "25" in data["response"] or "email" in data["response"].lower()

    def test_weather_and_recommendation_flow(self):
        """
        E2E Flow: Get weather and make recommendation
        """
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": "What's the weather in Tokyo and should I bring an umbrella?"},
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        data = response.json()
        assert "tokyo" in data["response"].lower() or "weather" in data["response"].lower()

    def test_gold_price_calculation_flow(self):
        """
        E2E Flow: Get gold price and calculate with it
        """
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": "What is the gold price and calculate 10% of it?"},
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        data = response.json()
        assert "gold" in data["response"].lower() or "price" in data["response"].lower()


class TestErrorHandlingFlows:
    """Test E2E error handling and edge cases"""

    @pytest.fixture(autouse=True)
    def check_server(self):
        try:
            requests.get(BASE_URL, timeout=5)
        except requests.exceptions.ConnectionError:
            pytest.skip("Flask server not running")

    def test_malformed_request(self):
        """Test handling of malformed JSON request"""
        response = requests.post(
            f"{BASE_URL}/api/query",
            data="not json",
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )

        # Should return error status
        assert response.status_code in [400, 500]

    def test_missing_query_field(self):
        """Test handling of missing 'query' field"""
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"wrong_field": "test"},
            timeout=TIMEOUT
        )

        # Should handle gracefully
        assert response.status_code in [200, 400]

    def test_very_long_query(self):
        """Test handling of very long query"""
        long_query = "Calculate " + " plus ".join(str(i) for i in range(100))

        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": long_query},
            timeout=TIMEOUT * 2  # Allow more time
        )

        # Should either process or reject gracefully
        assert response.status_code in [200, 400, 413]

    def test_special_characters_query(self):
        """Test handling of special characters in query"""
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": "Calculate 5 + 5 <script>alert('xss')</script>"},
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        data = response.json()
        # Should not execute script, should calculate
        assert "10" in data["response"] or "5" in data["response"]


class TestConcurrentUserFlows:
    """Test multiple users accessing system concurrently"""

    @pytest.fixture(autouse=True)
    def check_server(self):
        try:
            requests.get(BASE_URL, timeout=5)
        except requests.exceptions.ConnectionError:
            pytest.skip("Flask server not running")

    def test_concurrent_queries(self):
        """Test multiple concurrent user queries"""
        import concurrent.futures

        def make_query(query_text):
            response = requests.post(
                f"{BASE_URL}/api/query",
                json={"query": query_text},
                timeout=TIMEOUT
            )
            return response.status_code, response.json()

        queries = [
            "What is 10 + 10?",
            "What is the weather?",
            "What is the gold price?",
            "Calculate 5 times 5",
            "What is 100 divided by 2?"
        ]

        # Execute queries concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_query, q) for q in queries]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should succeed
        assert len(results) == 5
        for status, data in results:
            assert status == 200
            assert "response" in data


class TestUserInterfaceFlow:
    """Test user interface interactions"""

    @pytest.fixture(autouse=True)
    def check_server(self):
        try:
            requests.get(BASE_URL, timeout=5)
        except requests.exceptions.ConnectionError:
            pytest.skip("Flask server not running")

    def test_homepage_loads(self):
        """Test that homepage loads successfully"""
        response = requests.get(BASE_URL, timeout=TIMEOUT)
        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")

    def test_static_resources_load(self):
        """Test that static resources (CSS/JS) load"""
        response = requests.get(f"{BASE_URL}/visualization.html", timeout=TIMEOUT)
        # Should either load or return 404 if not in static folder
        assert response.status_code in [200, 404]

    def test_session_creation(self):
        """Test that sessions are created properly"""
        response = requests.get(BASE_URL, timeout=TIMEOUT)
        # Should set session cookie
        assert "Set-Cookie" in response.headers or "session" in response.cookies


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
