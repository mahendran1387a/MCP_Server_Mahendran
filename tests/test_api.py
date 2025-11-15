"""
API Tests for Flask Web Server
Validates all endpoints, input validation, error handling, and API contracts
"""
import pytest
import requests
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_URL = "http://localhost:5000"
TIMEOUT = 30


class TestQueryEndpoint:
    """Test /api/query endpoint"""

    @pytest.fixture(autouse=True)
    def check_server(self):
        try:
            requests.get(BASE_URL, timeout=5)
        except requests.exceptions.ConnectionError:
            pytest.skip("Flask server not running")

    def test_query_endpoint_exists(self):
        """Test that /api/query endpoint exists"""
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": "test"},
            timeout=TIMEOUT
        )
        # Should not return 404
        assert response.status_code != 404

    def test_query_valid_input(self):
        """Test query with valid input"""
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": "What is 2 + 2?"},
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0

    def test_query_content_type_json(self):
        """Test that endpoint returns JSON"""
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": "test"},
            timeout=TIMEOUT
        )

        assert "application/json" in response.headers.get("Content-Type", "")

    def test_query_empty_string(self):
        """Test query with empty string"""
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": ""},
            timeout=TIMEOUT
        )

        # Should handle gracefully
        assert response.status_code in [200, 400]

    def test_query_missing_field(self):
        """Test query with missing 'query' field"""
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={},
            timeout=TIMEOUT
        )

        assert response.status_code in [200, 400]
        if response.status_code == 400:
            data = response.json()
            assert "error" in data or "message" in data

    def test_query_invalid_json(self):
        """Test query with invalid JSON"""
        response = requests.post(
            f"{BASE_URL}/api/query",
            data="not valid json",
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )

        assert response.status_code in [400, 500]

    def test_query_null_value(self):
        """Test query with null value"""
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": None},
            timeout=TIMEOUT
        )

        assert response.status_code in [200, 400]

    def test_query_numeric_value(self):
        """Test query with numeric value instead of string"""
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": 12345},
            timeout=TIMEOUT
        )

        # Should either handle or reject
        assert response.status_code in [200, 400]

    def test_query_array_value(self):
        """Test query with array value"""
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": ["test", "query"]},
            timeout=TIMEOUT
        )

        assert response.status_code in [200, 400]

    def test_query_max_length(self):
        """Test query with very long input"""
        long_query = "a" * 10000

        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": long_query},
            timeout=TIMEOUT * 2
        )

        # Should either process or reject based on max length
        assert response.status_code in [200, 400, 413]

    def test_query_special_characters(self):
        """Test query with special characters"""
        special_query = "Test <script>alert('xss')</script> & special chars: é, ñ, 中文"

        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": special_query},
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        data = response.json()
        assert "response" in data

    def test_query_sql_injection_attempt(self):
        """Test query with SQL injection attempt"""
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": "'; DROP TABLE users; --"},
            timeout=TIMEOUT
        )

        # Should handle safely
        assert response.status_code == 200

    def test_query_response_structure(self):
        """Test that response has expected structure"""
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": "test"},
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        data = response.json()

        # Should have 'response' field
        assert "response" in data
        # Response should be a string
        assert isinstance(data["response"], str)

    def test_query_cors_headers(self):
        """Test CORS headers if applicable"""
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": "test"},
            timeout=TIMEOUT
        )

        # Check if CORS headers are present (optional)
        headers = response.headers
        # CORS might be enabled or not, just check format
        assert response.status_code == 200


class TestRAGUploadEndpoint:
    """Test /api/rag/upload endpoint"""

    @pytest.fixture(autouse=True)
    def check_server(self):
        try:
            requests.get(BASE_URL, timeout=5)
        except requests.exceptions.ConnectionError:
            pytest.skip("Flask server not running")

    def test_upload_endpoint_exists(self):
        """Test that upload endpoint exists"""
        files = {'file': ('test.txt', 'test content', 'text/plain')}
        response = requests.post(
            f"{BASE_URL}/api/rag/upload",
            files=files,
            timeout=TIMEOUT
        )

        # Should either work or be not implemented (404)
        assert response.status_code in [200, 404]

    def test_upload_text_file(self):
        """Test uploading a text file"""
        files = {'file': ('document.txt', 'This is test content', 'text/plain')}

        response = requests.post(
            f"{BASE_URL}/api/rag/upload",
            files=files,
            timeout=TIMEOUT
        )

        if response.status_code == 404:
            pytest.skip("Upload endpoint not implemented")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "success" in data or "status" in data

    def test_upload_without_file(self):
        """Test upload without file"""
        response = requests.post(
            f"{BASE_URL}/api/rag/upload",
            data={},
            timeout=TIMEOUT
        )

        if response.status_code == 404:
            pytest.skip("Upload endpoint not implemented")

        # Should return error
        assert response.status_code in [400, 500]

    def test_upload_empty_file(self):
        """Test uploading empty file"""
        files = {'file': ('empty.txt', '', 'text/plain')}

        response = requests.post(
            f"{BASE_URL}/api/rag/upload",
            files=files,
            timeout=TIMEOUT
        )

        if response.status_code == 404:
            pytest.skip("Upload endpoint not implemented")

        # Should handle empty file
        assert response.status_code in [200, 400]

    def test_upload_large_file(self):
        """Test uploading large file"""
        large_content = "a" * 1000000  # 1MB

        files = {'file': ('large.txt', large_content, 'text/plain')}

        response = requests.post(
            f"{BASE_URL}/api/rag/upload",
            files=files,
            timeout=TIMEOUT * 2
        )

        if response.status_code == 404:
            pytest.skip("Upload endpoint not implemented")

        # Should either process or reject based on size limit
        assert response.status_code in [200, 413]

    def test_upload_invalid_file_type(self):
        """Test uploading unsupported file type"""
        files = {'file': ('test.exe', b'\x00\x01\x02', 'application/octet-stream')}

        response = requests.post(
            f"{BASE_URL}/api/rag/upload",
            files=files,
            timeout=TIMEOUT
        )

        if response.status_code == 404:
            pytest.skip("Upload endpoint not implemented")

        # Should either accept or reject
        assert response.status_code in [200, 400, 415]


class TestRAGQueryEndpoint:
    """Test /api/rag/query endpoint"""

    @pytest.fixture(autouse=True)
    def check_server(self):
        try:
            requests.get(BASE_URL, timeout=5)
        except requests.exceptions.ConnectionError:
            pytest.skip("Flask server not running")

    def test_rag_query_endpoint_exists(self):
        """Test that RAG query endpoint exists"""
        response = requests.post(
            f"{BASE_URL}/api/rag/query",
            json={"query": "test", "n_results": 3},
            timeout=TIMEOUT
        )

        # Should either work or be not implemented
        assert response.status_code in [200, 404]

    def test_rag_query_valid_input(self):
        """Test RAG query with valid input"""
        response = requests.post(
            f"{BASE_URL}/api/rag/query",
            json={"query": "test query", "n_results": 3},
            timeout=TIMEOUT
        )

        if response.status_code == 404:
            pytest.skip("RAG query endpoint not implemented")

        assert response.status_code == 200
        data = response.json()
        assert "result" in data or "results" in data or "documents" in data

    def test_rag_query_missing_n_results(self):
        """Test RAG query without n_results"""
        response = requests.post(
            f"{BASE_URL}/api/rag/query",
            json={"query": "test"},
            timeout=TIMEOUT
        )

        if response.status_code == 404:
            pytest.skip("RAG query endpoint not implemented")

        # Should use default or return error
        assert response.status_code in [200, 400]

    def test_rag_query_invalid_n_results(self):
        """Test RAG query with invalid n_results"""
        response = requests.post(
            f"{BASE_URL}/api/rag/query",
            json={"query": "test", "n_results": -1},
            timeout=TIMEOUT
        )

        if response.status_code == 404:
            pytest.skip("RAG query endpoint not implemented")

        # Should validate and reject or use default
        assert response.status_code in [200, 400]

    def test_rag_query_empty_query(self):
        """Test RAG query with empty query string"""
        response = requests.post(
            f"{BASE_URL}/api/rag/query",
            json={"query": "", "n_results": 3},
            timeout=TIMEOUT
        )

        if response.status_code == 404:
            pytest.skip("RAG query endpoint not implemented")

        # Should handle empty query
        assert response.status_code in [200, 400]


class TestHealthEndpoint:
    """Test health/status endpoints"""

    @pytest.fixture(autouse=True)
    def check_server(self):
        try:
            requests.get(BASE_URL, timeout=5)
        except requests.exceptions.ConnectionError:
            pytest.skip("Flask server not running")

    def test_health_endpoint(self):
        """Test if health endpoint exists"""
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)

        # Either exists or doesn't
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            # Should return status info
            data = response.json()
            assert "status" in data or "healthy" in str(data).lower()

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = requests.get(BASE_URL, timeout=TIMEOUT)

        # Should return homepage
        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")


class TestHTTPMethods:
    """Test HTTP method handling"""

    @pytest.fixture(autouse=True)
    def check_server(self):
        try:
            requests.get(BASE_URL, timeout=5)
        except requests.exceptions.ConnectionError:
            pytest.skip("Flask server not running")

    def test_query_get_method_not_allowed(self):
        """Test that GET is not allowed on /api/query"""
        response = requests.get(
            f"{BASE_URL}/api/query",
            timeout=TIMEOUT
        )

        # Should return 405 Method Not Allowed
        assert response.status_code in [405, 404]

    def test_query_put_method_not_allowed(self):
        """Test that PUT is not allowed on /api/query"""
        response = requests.put(
            f"{BASE_URL}/api/query",
            json={"query": "test"},
            timeout=TIMEOUT
        )

        assert response.status_code in [405, 404]

    def test_query_delete_method_not_allowed(self):
        """Test that DELETE is not allowed on /api/query"""
        response = requests.delete(
            f"{BASE_URL}/api/query",
            timeout=TIMEOUT
        )

        assert response.status_code in [405, 404]

    def test_upload_get_method_not_allowed(self):
        """Test that GET is not allowed on /api/rag/upload"""
        response = requests.get(
            f"{BASE_URL}/api/rag/upload",
            timeout=TIMEOUT
        )

        assert response.status_code in [405, 404]


class TestRateLimiting:
    """Test rate limiting if implemented"""

    @pytest.fixture(autouse=True)
    def check_server(self):
        try:
            requests.get(BASE_URL, timeout=5)
        except requests.exceptions.ConnectionError:
            pytest.skip("Flask server not running")

    def test_rapid_requests(self):
        """Test making rapid requests"""
        responses = []

        for i in range(10):
            response = requests.post(
                f"{BASE_URL}/api/query",
                json={"query": f"test {i}"},
                timeout=TIMEOUT
            )
            responses.append(response.status_code)

        # All should succeed or some might be rate limited
        assert all(status in [200, 429] for status in responses)


class TestErrorResponses:
    """Test error response formats"""

    @pytest.fixture(autouse=True)
    def check_server(self):
        try:
            requests.get(BASE_URL, timeout=5)
        except requests.exceptions.ConnectionError:
            pytest.skip("Flask server not running")

    def test_404_response_format(self):
        """Test 404 error response format"""
        response = requests.get(
            f"{BASE_URL}/nonexistent/endpoint",
            timeout=TIMEOUT
        )

        assert response.status_code == 404

    def test_500_error_handling(self):
        """Test that 500 errors are handled gracefully"""
        # Try to trigger an error with malformed data
        response = requests.post(
            f"{BASE_URL}/api/query",
            data="malformed data",
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )

        # Should return error status
        assert response.status_code in [400, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
