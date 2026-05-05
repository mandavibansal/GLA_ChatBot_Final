"""
chatbot.py
Saare pieces ko jodta hai — yahi main brain hai chatbot ka.

Flow:
User query → Retriever (relevant chunks) → Groq LLM → Answer

Supports both traditional FAISS retrieval and hybrid FAISS+Supermemory retrieval.
"""

from retriever import GlaRetriever
from groq_llm import GroqLLM
from typing import Optional, Literal

# Try to import hybrid retriever, but make it optional
try:
    from hybrid_retriever import HybridRetriever
    HYBRID_AVAILABLE = True
except ImportError:
    HYBRID_AVAILABLE = False


class GLAChatbot:
    """
    GLA Admission Chatbot — retriever + LLM ka combination.
    Supports both traditional and hybrid (FAISS + Supermemory) retrieval.

    Usage:
        bot = GLAChatbot(retrieval_mode="hybrid")  # or "faiss"
        answer = bot.ask("What are the B.Tech fees?")
        print(answer)
    """

    def __init__(
        self,
        vector_store_dir: str = "vector_store",
        model: str = "llama-3.1-8b-instant",
        retrieval_mode: Literal["faiss", "hybrid"] = "faiss",
        supermemory_api_key: Optional[str] = None
    ):
        print("GLA Chatbot initialize ho raha hai...")

        # Select retriever based on mode
        if retrieval_mode == "hybrid" and HYBRID_AVAILABLE:
            print("  ℹ️  Using Hybrid Retrieval (FAISS + Supermemory)")
            self.retriever = HybridRetriever(
                vector_store_dir=vector_store_dir,
                supermemory_api_key=supermemory_api_key
            )
            self.retrieval_mode = "hybrid"
        else:
            if retrieval_mode == "hybrid" and not HYBRID_AVAILABLE:
                print("  ⚠️  Hybrid mode requested but not available. Falling back to FAISS.")
            else:
                print("  ℹ️  Using FAISS Vector Retrieval")
            self.retriever = GlaRetriever(vector_store_dir)
            self.retrieval_mode = "faiss"

        self.llm = GroqLLM(model=model)
        self.chat_history: list[dict] = []
        print("  ✓ Chatbot ready!\n")

    def ask(self, user_query: str, use_history: bool = True) -> str:
        """
        User ka sawal lo, answer wapas do.
        """
        if not user_query.strip():
            return "Please ask a question!"

        # Get context based on retrieval mode
        if self.retrieval_mode == "hybrid":
            context = self.retriever.retrieve_and_format_hybrid(user_query)
        else:
            context = self.retriever.retrieve_and_format(user_query)

        if use_history and self.chat_history:
            answer = self.llm.generate_with_history(
                user_query, context, self.chat_history
            )
        else:
            answer = self.llm.generate(user_query, context)

        self.chat_history.append({"role": "user", "content": user_query})
        self.chat_history.append({"role": "assistant", "content": answer})
        if len(self.chat_history) > 20:
            self.chat_history = self.chat_history[-20:]

        # Update memory graph if using hybrid mode
        if self.retrieval_mode == "hybrid":
            self.retriever.update_memory_with_response(user_query, answer)

        return answer

    def ask_with_sources(self, user_query: str) -> dict:
        """
        Answer ke saath source chunks bhi chahiye toh ye use karo.

        Returns:
            {
                "answer": "...",
                "sources": ["brochure.pdf", ...],
                "chunks": ["chunk text...", ...]
            }
        """
        if self.retrieval_mode == "hybrid":
            hybrid_results = self.retriever.retrieve_hybrid(user_query)
            context = self.retriever.retrieve_and_format_hybrid(user_query)
            answer = self.llm.generate(user_query, context)

            sources = []
            chunks = []
            for result in hybrid_results:
                metadata = result.get("metadata", {})
                source = metadata.get("source") if isinstance(metadata, dict) else None
                if source:
                    sources.append(source)
                chunks.append(result.get("content", "")[:200])

            return {
                "answer": answer,
                "sources": list(dict.fromkeys(sources)),
                "chunks": chunks,
            }

        docs = self.retriever.get_relevant_chunks(user_query)
        context = self.retriever.format_context(docs)
        answer = self.llm.generate(user_query, context)

        return {
            "answer": answer,
            "sources": list({doc.metadata.get("source", "?") for doc in docs}),
            "chunks": [doc.page_content[:200] for doc in docs],
        }

    def reset_history(self):
        """Conversation history clear karo."""
        self.chat_history = []
        print("Chat history cleared.")

    def get_history(self) -> list[dict]:
        """Current conversation history return karo."""
        return self.chat_history.copy()


def run_cli():
    """Terminal mein chatbot chalao."""
    print("=" * 55)
    print("  GLA University Admission Chatbot")
    print("  Type 'quit' to exit | 'clear' to reset history")
    print("=" * 55)

    bot = GLAChatbot()

    while True:
        try:
            query = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nChatbot closed. Goodbye!")
            break

        if not query:
            continue

        if query.lower() in ("quit", "exit", "bye"):
            print("Thank you! Welcome to GLA University. 🎓")
            break

        if query.lower() == "clear":
            bot.reset_history()
            continue

        answer = bot.ask(query)
        print(f"\nChatbot: {answer}")


if __name__ == "__main__":
    run_cli()