"""
memory_graph.py
Supermemory integration for memory graph-based retrieval.
Enhances retrieval with entity search and profile-based context.
"""

import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


class SupermemoryMemoryGraph:
    """
    Supermemory memory graph wrapper.

    Uses the official `supermemory` SDK and exposes:
      - document search (search.documents)
      - profile retrieval (profile)
      - memory addition (add)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        container_tag: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("SUPERMEMORY_API_KEY")
        self.container_tag = container_tag

        if not self.api_key:
            print("⚠️  SUPERMEMORY_API_KEY not found. Memory graph features will be limited.")
            self.initialized = False
            return

        try:
            from supermemory import Supermemory
            self.client = Supermemory(api_key=self.api_key)
            self.initialized = True
            print("  ✓ Supermemory client initialized")
        except ImportError:
            print("⚠️  Supermemory not installed. Install with: pip install supermemory")
            self.initialized = False
        except Exception as e:
            print(f"⚠️  Failed to initialize Supermemory: {e}")
            self.initialized = False

    def add_to_memory(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        custom_id: Optional[str] = None,
        task_type: str = "memory"
    ) -> bool:
        if not self.initialized:
            return False

        try:
            add_kwargs = {
                "content": content,
                "metadata": metadata or {},
                "task_type": task_type,
            }
            if self.container_tag is not None:
                add_kwargs["container_tags"] = [self.container_tag]
            if custom_id is not None:
                add_kwargs["custom_id"] = custom_id

            self.client.add(**add_kwargs)
            return True
        except Exception as e:
            print(f"Error adding to Supermemory: {e}")
            return False

    def retrieve_by_entities(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        if not self.initialized:
            return []

        try:
            search_kwargs = {
                "q": query,
                "limit": top_k,
                "include_full_docs": True,
                "rerank": True,
            }
            if self.container_tag:
                search_kwargs["container_tags"] = [self.container_tag]

            response = self.client.search.documents(**search_kwargs)

            results = []
            for item in getattr(response, "results", []):
                results.append({
                    "content": item.content or self._join_chunks(item.chunks),
                    "score": getattr(item, "score", 0.0),
                    "metadata": item.metadata or {},
                    "title": getattr(item, "title", None),
                    "document_id": getattr(item, "document_id", None),
                })

            if not results and self.container_tag:
                # retry without container tag if no items were found
                response = self.client.search.documents(
                    q=query,
                    limit=top_k,
                    include_full_docs=True,
                    rerank=True,
                )
                results = []
                for item in getattr(response, "results", []):
                    results.append({
                        "content": item.content or self._join_chunks(item.chunks),
                        "score": getattr(item, "score", 0.0),
                        "metadata": item.metadata or {},
                        "title": getattr(item, "title", None),
                        "document_id": getattr(item, "document_id", None),
                    })
            return results
        except Exception as e:
            print(f"Error retrieving from Supermemory: {e}")
            return []

    def retrieve_profile_context(
        self,
        query: str,
        container_tag: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.initialized:
            return {}

        try:
            response = self.client.profile(
                container_tag=container_tag or self.container_tag,
                q=query,
            )
            profile = response.profile
            return {
                "static": list(getattr(profile, "static", []) or []),
                "dynamic": list(getattr(profile, "dynamic", []) or []),
                "search_results": getattr(response, "search_results", None),
            }
        except Exception as e:
            print(f"Error retrieving profile from Supermemory: {e}")
            return {}

    def get_entity_relationships(self, query: str) -> Dict[str, Any]:
        return self.retrieve_profile_context(query)

    def _join_chunks(self, chunks: Any) -> str:
        if not chunks:
            return ""
        if isinstance(chunks, list):
            return "\n\n".join(getattr(chunk, "content", str(chunk)) for chunk in chunks)
        return str(chunks)

    def context_from_memory(self, query: str, top_k: int = 4) -> str:
        results = self.retrieve_by_entities(query, top_k=top_k)
        if not results:
            return ""

        parts = []
        for i, result in enumerate(results, 1):
            parts.append(
                f"[Memory {i} | Score: {result.get('score', 0):.2f}]\n{result.get('content', '').strip()}"
            )
        return "\n\n---\n\n".join(parts)

    def update_conversation_memory(
        self,
        user_query: str,
        assistant_response: str
    ) -> bool:
        return self.add_to_memory(
            content=assistant_response,
            metadata={
                "type": "conversation",
                "user_query": user_query,
                "role": "assistant",
            },
            task_type="memory"
        )

    def clear_memory(self) -> bool:
        print("⚠️  Supermemory clear operation is not implemented in this wrapper.")
        return False
