"""
Memory and Context Management System
Provides conversation history, context persistence, and intelligent memory
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import pickle


class ConversationMemory:
    """Manages conversation history and context"""

    def __init__(self, storage_path: str = "./data/memory"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.conversations = {}  # session_id -> messages
        self.session_metadata = {}  # session_id -> metadata
        self.current_session = None

    def create_session(self, session_id: Optional[str] = None) -> str:
        """Create new conversation session"""
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.conversations[session_id] = []
        self.session_metadata[session_id] = {
            'created_at': datetime.now().isoformat(),
            'message_count': 0,
            'tokens_used': 0
        }
        self.current_session = session_id

        return session_id

    def add_message(self, role: str, content: str,
                   session_id: Optional[str] = None,
                   metadata: Optional[Dict] = None):
        """Add message to conversation history"""
        if session_id is None:
            session_id = self.current_session

        if session_id not in self.conversations:
            self.create_session(session_id)

        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        self.conversations[session_id].append(message)
        self.session_metadata[session_id]['message_count'] += 1

    def get_history(self, session_id: Optional[str] = None,
                   limit: Optional[int] = None) -> List[Dict]:
        """Get conversation history"""
        if session_id is None:
            session_id = self.current_session

        if session_id not in self.conversations:
            return []

        messages = self.conversations[session_id]

        if limit:
            return messages[-limit:]

        return messages

    def get_context_window(self, session_id: Optional[str] = None,
                          max_messages: int = 10) -> List[Dict]:
        """Get recent context window for LLM"""
        return self.get_history(session_id, limit=max_messages)

    def save_session(self, session_id: Optional[str] = None):
        """Save session to disk"""
        if session_id is None:
            session_id = self.current_session

        if session_id not in self.conversations:
            return

        session_file = self.storage_path / f"{session_id}.json"

        session_data = {
            'session_id': session_id,
            'metadata': self.session_metadata[session_id],
            'messages': self.conversations[session_id]
        }

        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)

    def load_session(self, session_id: str) -> bool:
        """Load session from disk"""
        session_file = self.storage_path / f"{session_id}.json"

        if not session_file.exists():
            return False

        with open(session_file, 'r') as f:
            session_data = json.load(f)

        self.conversations[session_id] = session_data['messages']
        self.session_metadata[session_id] = session_data['metadata']
        self.current_session = session_id

        return True

    def list_sessions(self) -> List[Dict]:
        """List all saved sessions"""
        sessions = []

        for session_file in self.storage_path.glob("session_*.json"):
            with open(session_file, 'r') as f:
                data = json.load(f)
                sessions.append({
                    'session_id': data['session_id'],
                    'created_at': data['metadata']['created_at'],
                    'message_count': data['metadata']['message_count']
                })

        return sorted(sessions, key=lambda x: x['created_at'], reverse=True)

    def search_history(self, query: str,
                      session_id: Optional[str] = None) -> List[Dict]:
        """Search conversation history for query"""
        if session_id:
            sessions_to_search = [session_id]
        else:
            sessions_to_search = list(self.conversations.keys())

        results = []

        for sid in sessions_to_search:
            if sid not in self.conversations:
                continue

            for msg in self.conversations[sid]:
                if query.lower() in msg['content'].lower():
                    results.append({
                        'session_id': sid,
                        'message': msg
                    })

        return results

    def summarize_session(self, session_id: Optional[str] = None) -> str:
        """Generate simple summary of session"""
        if session_id is None:
            session_id = self.current_session

        if session_id not in self.conversations:
            return "No session found"

        messages = self.conversations[session_id]
        metadata = self.session_metadata[session_id]

        user_messages = [m for m in messages if m['role'] == 'user']
        assistant_messages = [m for m in messages if m['role'] == 'assistant']

        summary = f"""Session Summary ({session_id})
Created: {metadata['created_at']}
Total Messages: {metadata['message_count']}
User Messages: {len(user_messages)}
Assistant Messages: {len(assistant_messages)}

Recent Topics:
"""
        # Simple topic extraction: first few words of recent user messages
        for msg in user_messages[-5:]:
            preview = msg['content'][:50]
            summary += f"- {preview}...\n"

        return summary


class SemanticMemory:
    """Long-term semantic memory using vector store"""

    def __init__(self, store_path: str = "./data/semantic_memory"):
        from vector_store import VectorStore

        self.vector_store = VectorStore(store_path=store_path,
                                       model_name="all-MiniLM-L6-v2")
        self.initialized = False

    def initialize(self):
        """Initialize semantic memory"""
        self.vector_store.initialize()
        self.initialized = True

    def store_fact(self, fact: str, metadata: Optional[Dict] = None):
        """Store a fact in semantic memory"""
        if not self.initialized:
            self.initialize()

        meta = metadata or {}
        meta['stored_at'] = datetime.now().isoformat()
        meta['type'] = 'fact'

        self.vector_store.add_documents([fact], [meta])

    def store_conversation_summary(self, summary: str, session_id: str):
        """Store conversation summary"""
        if not self.initialized:
            self.initialize()

        metadata = {
            'type': 'conversation_summary',
            'session_id': session_id,
            'stored_at': datetime.now().isoformat()
        }

        self.vector_store.add_documents([summary], [metadata])

    def recall(self, query: str, k: int = 5) -> List[Dict]:
        """Recall relevant facts from memory"""
        if not self.initialized:
            self.initialize()

        return self.vector_store.search(query, k=k)

    def get_stats(self) -> Dict:
        """Get memory statistics"""
        return self.vector_store.get_stats()


class ContextManager:
    """Manages conversation context and memory"""

    def __init__(self):
        self.conversation_memory = ConversationMemory()
        self.semantic_memory = SemanticMemory()
        self.working_memory = {}  # Temporary context

    def initialize(self):
        """Initialize context manager"""
        self.semantic_memory.initialize()

    def add_to_working_memory(self, key: str, value: Any):
        """Add temporary context"""
        self.working_memory[key] = value

    def get_from_working_memory(self, key: str) -> Any:
        """Get temporary context"""
        return self.working_memory.get(key)

    def clear_working_memory(self):
        """Clear temporary context"""
        self.working_memory = {}

    def build_context(self, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Build complete context for query"""

        # Get conversation history
        recent_history = self.conversation_memory.get_context_window(
            session_id, max_messages=10
        )

        # Recall relevant facts from semantic memory
        relevant_facts = self.semantic_memory.recall(query, k=3)

        # Combine into context
        context = {
            'query': query,
            'recent_history': recent_history,
            'relevant_facts': relevant_facts,
            'working_memory': self.working_memory,
            'session_id': session_id or self.conversation_memory.current_session
        }

        return context

    def save_state(self):
        """Save all state"""
        self.conversation_memory.save_session()
        self.semantic_memory.vector_store.save()
