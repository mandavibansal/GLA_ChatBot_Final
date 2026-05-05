"""
hybrid_retriever.py
Combines FAISS vector retrieval with Supermemory memory graph.
Provides enhanced context by leveraging both semantic and entity-based retrieval.
"""

from langchain_core.documents import Document
from retriever import GlaRetriever
from memory_graph import SupermemoryMemoryGraph
from typing import Optional


class HybridRetriever:
    """
    Hybrid retriever combining FAISS (vector similarity) + Supermemory (memory graph).
    Uses both techniques to provide richer context for better responses.
    """

    def __init__(
        self,
        vector_store_dir: str = "vector_store",
        supermemory_api_key: Optional[str] = None,
        supermemory_container_tag: Optional[str] = None,
        faiss_weight: float = 0.6,
        memory_weight: float = 0.4
    ):
        """
        Initialize hybrid retriever.

        Args:
            vector_store_dir: Path to FAISS vector store
            supermemory_api_key: API key for Supermemory (optional)
            supermemory_container_tag: Container tag for Supermemory search/profile
            faiss_weight: Weight for FAISS results (0-1)
            memory_weight: Weight for memory graph results (0-1)
        """
        print("🔄 Initializing Hybrid Retriever (FAISS + Supermemory)...")

        self.faiss_retriever = GlaRetriever(vector_store_dir)
        self.memory_graph = SupermemoryMemoryGraph(
            api_key=supermemory_api_key,
            container_tag=supermemory_container_tag,
        )

        # Normalize weights
        total = faiss_weight + memory_weight
        self.faiss_weight = faiss_weight / total
        self.memory_weight = memory_weight / total

        print(f"  ✓ FAISS weight: {self.faiss_weight:.1%}")
        print(f"  ✓ Memory graph weight: {self.memory_weight:.1%}")
        print("  ✓ Hybrid retriever ready\n")

    def retrieve_hybrid(self, query: str, top_k: int = 4) -> list[dict]:
        """
        Retrieve results from both FAISS and Supermemory, combined intelligently.

        Args:
            query: User query
            top_k: Number of results to return

        Returns:
            List of combined results with scores
        """
        results = []

        # Get FAISS results (vector similarity)
        faiss_results = self._get_faiss_results(query, top_k)
        for result in faiss_results:
            result["source"] = "faiss"
            result["combined_score"] = result["score"] * self.faiss_weight
            results.append(result)

        # Get Supermemory results (memory graph)
        memory_results = self._get_memory_results(query, top_k)
        for result in memory_results:
            result["source"] = "supermemory"
            result["combined_score"] = result.get("score", 0.5) * self.memory_weight
            results.append(result)

        # Sort by combined score and deduplicate
        results = self._deduplicate_results(results)
        results.sort(key=lambda x: x["combined_score"], reverse=True)

        return results[:top_k]

    def retrieve_and_format_hybrid(self, query: str, top_k: int = 4) -> str:
        """
        Retrieve from both sources and format as context string.

        Args:
            query: User query
            top_k: Number of results to return

        Returns:
            Formatted context string
        """
        results = self.retrieve_hybrid(query, top_k)

        if not results:
            return "No relevant information found."

        parts = []
        for i, result in enumerate(results, 1):
            source_label = result["source"].upper()
            content = result.get("content", result.get("page_content", ""))
            score = result.get("combined_score", 0)

            parts.append(
                f"[{source_label} | Match: {score:.1%}]\n{content.strip()}"
            )

        return "\n\n---\n\n".join(parts)

    def get_relevant_chunks(self, query: str, top_k: int = 4) -> list[Document]:
        """
        Return relevant FAISS document chunks for compatibility with GlaRetriever.
        """
        return self.faiss_retriever.get_relevant_chunks(query)

    def format_context(self, docs: list[Document]) -> str:
        """
        Format FAISS document chunks as context.
        """
        return self.faiss_retriever.format_context(docs)

    def retrieve_and_format(self, query: str, top_k: int = 4) -> str:
        """
        Compatibility wrapper that runs hybrid retrieval and formatting.
        """
        return self.retrieve_and_format_hybrid(query, top_k)

    def _get_faiss_results(self, query: str, top_k: int) -> list[dict]:
        """Get results from FAISS."""
        try:
            docs_with_scores = self.faiss_retriever.get_chunks_with_scores(
                query, k=top_k
            )

            results = []
            for doc, score in docs_with_scores:
                results.append({
                    "content": doc.page_content,
                    "score": score,
                    "metadata": doc.metadata
                })
            return results
        except TypeError:
            # Fallback for older retriever API signatures
            docs_with_scores = self.faiss_retriever.get_chunks_with_scores(query)
            results = []
            for doc, score in docs_with_scores[:top_k]:
                results.append({
                    "content": doc.page_content,
                    "score": score,
                    "metadata": doc.metadata
                })
            return results
        except Exception as e:
            print(f"Error retrieving from FAISS: {e}")
            return []

    def _get_memory_results(self, query: str, top_k: int) -> list[dict]:
        """Get results from Supermemory memory graph."""
        if not self.memory_graph.initialized:
            return []

        try:
            results = self.memory_graph.retrieve_by_entities(query, top_k=top_k)
            return results or []
        except Exception as e:
            print(f"Error retrieving from memory graph: {e}")
            return []

    def _deduplicate_results(self, results: list[dict]) -> list[dict]:
        """Remove duplicate results based on content similarity."""
        seen = set()
        deduplicated = []

        for result in results:
            content = result.get("content", "")[:100]  # First 100 chars for comparison
            if content not in seen:
                seen.add(content)
                deduplicated.append(result)

        return deduplicated

    def add_document_to_memory(self, content: str, source: str) -> bool:
        """
        Add a document to Supermemory for future retrieval.

        Args:
            content: Document content
            source: Source of document

        Returns:
            True if successful
        """
        metadata = {"source": source, "type": "document"}
        return self.memory_graph.add_to_memory(content, metadata=metadata)

    def get_entity_context(self, query: str) -> dict:
        """
        Get entity relationships from query.

        Args:
            query: User query

        Returns:
            Dictionary of entities and relationships
        """
        return self.memory_graph.get_entity_relationships(query)

    def update_memory_with_response(self, user_query: str, response: str) -> bool:
        """
        Update memory graph after a response.

        Args:
            user_query: User's original question
            response: Generated response

        Returns:
            True if successful
        """
        return self.memory_graph.update_conversation_memory(user_query, response)


if __name__ == "__main__":
    retriever = HybridRetriever()

    test_queries = [
        "B.Tech admission ke liye eligibility kya hai?",
        "GLA University mein fees kitni hai?",
        "Hostel facility hai kya?",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        context = retriever.retrieve_and_format_hybrid(query)
        print(context)
