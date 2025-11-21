"""
Async Client Manager for MCP clients in Flask
Manages client lifecycle properly in a background event loop
FIXED VERSION: Uses Python 3.13 compatible client
"""
import asyncio
import threading
from typing import Dict, Optional
from langchain_mcp_client_fixed import LangChainMCPClientFixed


class AsyncClientManager:
    """Manages async MCP clients in a background event loop"""

    def __init__(self):
        self.loop = None
        self.loop_thread = None
        self.clients: Dict[str, LangChainMCPClientFixed] = {}
        self.client_lock = threading.Lock()
        self._start_background_loop()

    def _start_background_loop(self):
        """Start the background event loop"""
        self.loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(
            target=self._run_loop,
            daemon=True
        )
        self.loop_thread.start()

    def _run_loop(self):
        """Run the event loop in the background thread"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _create_client(self, session_id: str, model_name: str = "llama3.2"):
        """Create and initialize a client (runs in background loop)"""
        client = LangChainMCPClientFixed(model_name=model_name)
        await client.initialize()
        self.clients[session_id] = client
        return client

    async def _query_client(self, session_id: str, query: str):
        """Query a client (runs in background loop)"""
        if session_id not in self.clients:
            raise RuntimeError(f"Client {session_id} not initialized")
        return await self.clients[session_id].process_query(query)

    async def _cleanup_client(self, session_id: str):
        """Cleanup a client (runs in background loop)"""
        if session_id in self.clients:
            client = self.clients[session_id]
            await client.cleanup()
            del self.clients[session_id]

    def initialize_client(self, session_id: str, model_name: str = "llama3.2", timeout: int = 30):
        """Initialize a client (called from Flask route)"""
        with self.client_lock:
            if session_id in self.clients:
                return  # Already initialized

        future = asyncio.run_coroutine_threadsafe(
            self._create_client(session_id, model_name),
            self.loop
        )
        future.result(timeout=timeout)

    def query(self, session_id: str, query: str, timeout: int = 120):
        """Query a client (called from Flask route)"""
        future = asyncio.run_coroutine_threadsafe(
            self._query_client(session_id, query),
            self.loop
        )
        return future.result(timeout=timeout)

    def cleanup_client(self, session_id: str, timeout: int = 5):
        """Cleanup a client (called from Flask route)"""
        if session_id not in self.clients:
            return

        future = asyncio.run_coroutine_threadsafe(
            self._cleanup_client(session_id),
            self.loop
        )
        try:
            future.result(timeout=timeout)
        except Exception as e:
            print(f"Warning: Error during client cleanup: {e}")

    def has_client(self, session_id: str) -> bool:
        """Check if a client exists"""
        return session_id in self.clients


# Global client manager instance
_manager: Optional[AsyncClientManager] = None


def get_client_manager() -> AsyncClientManager:
    """Get or create the global client manager"""
    global _manager
    if _manager is None:
        _manager = AsyncClientManager()
    return _manager
