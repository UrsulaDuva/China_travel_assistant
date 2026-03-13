"""
Memory System for Multi-Agent Conversation
==========================================

Provides conversation memory and vector-based semantic memory for agents.
"""

from typing import List, Dict, Any, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
import json
import os


class SimpleEmbeddings(Embeddings):
    """Simple embedding class for demo purposes.
    In production, use DashScope embeddings or other embedding models.
    """

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        # Simple hash-based embedding for demo
        # In production, use real embeddings like DashScope
        return [self._simple_embed(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        return self._simple_embed(text)

    def _simple_embed(self, text: str) -> List[float]:
        """Create a simple embedding vector."""
        # Use character frequencies as a simple embedding
        embedding = [0.0] * 256
        for char in text:
            embedding[ord(char) % 256] += 1.0
        # Normalize
        norm = sum(x * x for x in embedding) ** 0.5
        if norm > 0:
            embedding = [x / norm for x in embedding]
        return embedding


class ConversationMemory:
    """Manages conversation history for each session."""

    def __init__(self, session_id: str, max_history: int = 20):
        self.session_id = session_id
        self.max_history = max_history
        self.messages: List[Dict[str, Any]] = []
        self.trip_context: Dict[str, Any] = {}

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to history."""
        self.messages.append({
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "timestamp": self._get_timestamp()
        })
        # Trim history if needed
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]

    def update_trip_context(self, trip_spec: Dict[str, Any]):
        """Update trip planning context."""
        self.trip_context.update(trip_spec)

    def get_context_string(self) -> str:
        """Get context as a formatted string."""
        context_parts = []

        if self.trip_context:
            context_parts.append("当前行程信息：")
            if self.trip_context.get("destination_city"):
                context_parts.append(f"目的地：{self.trip_context['destination_city']}")
            if self.trip_context.get("start_date"):
                context_parts.append(f"出发日期：{self.trip_context['start_date']}")
            if self.trip_context.get("end_date"):
                context_parts.append(f"返程日期：{self.trip_context['end_date']}")
            if self.trip_context.get("num_travelers"):
                context_parts.append(f"出行人数：{self.trip_context['num_travelers']}")

        return "\n".join(context_parts)

    def get_history_string(self, max_messages: int = 5) -> str:
        """Get recent history as a formatted string."""
        recent = self.messages[-max_messages:] if len(self.messages) > max_messages else self.messages
        history_parts = []
        for msg in recent:
            role_cn = "用户" if msg["role"] == "user" else "助手"
            history_parts.append(f"{role_cn}：{msg['content']}")
        return "\n".join(history_parts)

    def to_langchain_messages(self) -> List[BaseMessage]:
        """Convert to LangChain message format."""
        lc_messages = []
        for msg in self.messages:
            if msg["role"] == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            else:
                lc_messages.append(AIMessage(content=msg["content"]))
        return lc_messages

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "session_id": self.session_id,
            "messages": self.messages,
            "trip_context": self.trip_context
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationMemory":
        """Deserialize from dictionary."""
        memory = cls(data["session_id"])
        memory.messages = data.get("messages", [])
        memory.trip_context = data.get("trip_context", {})
        return memory


class VectorMemory:
    """Vector-based semantic memory for long-term knowledge storage."""

    def __init__(self, persist_path: Optional[str] = None):
        self.persist_path = persist_path
        self.embeddings = SimpleEmbeddings()
        self.vectorstore: Optional[FAISS] = None
        self.documents: List[Dict[str, Any]] = []

    def add_document(self, text: str, metadata: Optional[Dict] = None):
        """Add a document to the vector store."""
        self.documents.append({
            "text": text,
            "metadata": metadata or {}
        })

        if self.vectorstore is None:
            self.vectorstore = FAISS.from_texts(
                [text],
                self.embeddings,
                metadatas=[metadata or {}]
            )
        else:
            self.vectorstore.add_texts([text], metadatas=[metadata or {}])

    def add_knowledge(self, category: str, content: str, source: str = ""):
        """Add structured knowledge."""
        self.add_document(
            text=content,
            metadata={
                "category": category,
                "source": source,
                "type": "knowledge"
            }
        )

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents."""
        if self.vectorstore is None:
            return []

        results = self.vectorstore.similarity_search_with_score(query, k=k)
        return [
            {
                "text": doc.page_content,
                "metadata": doc.metadata,
                "score": score
            }
            for doc, score in results
        ]

    def get_relevant_context(self, query: str, threshold: float = 0.8) -> str:
        """Get relevant context as a string."""
        results = self.search(query, k=3)
        if not results:
            return ""

        relevant = [r for r in results if r["score"] < threshold]
        if not relevant:
            return ""

        return "\n\n".join([
            f"[{r['metadata'].get('category', '知识')}]: {r['text']}"
            for r in relevant
        ])

    def save(self):
        """Persist the vector store."""
        if self.persist_path and self.vectorstore:
            os.makedirs(self.persist_path, exist_ok=True)
            self.vectorstore.save_local(self.persist_path)

    def load(self):
        """Load the vector store from disk."""
        if self.persist_path and os.path.exists(self.persist_path):
            self.vectorstore = FAISS.load_local(
                self.persist_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )


class MemoryManager:
    """Manages all session memories."""

    def __init__(self, persist_path: Optional[str] = None):
        self.persist_path = persist_path
        self.conversations: Dict[str, ConversationMemory] = {}
        self.vector_memory = VectorMemory(persist_path)

    def get_or_create_conversation(self, session_id: str) -> ConversationMemory:
        """Get or create conversation memory for a session."""
        if session_id not in self.conversations:
            self.conversations[session_id] = ConversationMemory(session_id)
        return self.conversations[session_id]

    def clear_conversation(self, session_id: str):
        """Clear conversation memory for a session."""
        if session_id in self.conversations:
            del self.conversations[session_id]

    def save_all(self):
        """Persist all memories."""
        self.vector_memory.save()
        # Could also save conversations to Redis or file