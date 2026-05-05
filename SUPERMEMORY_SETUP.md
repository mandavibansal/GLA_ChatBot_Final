# Supermemory Integration Guide

## Overview

Your GLA Chatbot now supports **hybrid retrieval** combining:
- **FAISS**: Vector similarity search (fast, semantic)
- **Supermemory**: Memory graph retrieval (entity relationships, knowledge graphs)

## Setup Instructions

### 1. Install Dependencies

Update your dependencies with Supermemory:

```bash
pip install -r requirements.txt
```

Or install just Supermemory:

```bash
pip install supermemory-py
```

### 2. Get Your Supermemory API Key

1. Visit [Supermemory](https://supermemory.ai) and sign up for an account
2. Navigate to your dashboard and generate an API key
3. Add it to your `.env` file:

```bash
SUPERMEMORY_API_KEY=your_api_key_here
```

### 3. Configuration

The chatbot automatically detects the API key from your `.env` file. No additional configuration needed!

## Usage

### In Streamlit App

1. **Start the app**:
   ```bash
   streamlit run app.py
   ```

2. **Select Retrieval Mode** in the sidebar:
   - **FAISS**: Traditional vector similarity (default, no API key needed)
   - **Hybrid**: FAISS + Supermemory memory graph (requires API key)

3. **Toggle "Show sources"** to see where information comes from:
   - `[FAISS | Match: 85%]` - From vector similarity
   - `[SUPERMEMORY | Match: 72%]` - From memory graph with entity relationships

### Programmatic Usage

```python
from chatbot import GLAChatbot

# Traditional FAISS retrieval
bot_faiss = GLAChatbot(retrieval_mode="faiss")
answer = bot_faiss.ask("What are the B.Tech fees?")

# Hybrid retrieval (requires API key)
bot_hybrid = GLAChatbot(
    retrieval_mode="hybrid",
    supermemory_api_key="your_key_here"
)
answer = bot_hybrid.ask("What are the B.Tech fees?")
```

### Using Hybrid Retriever Directly

```python
from hybrid_retriever import HybridRetriever

retriever = HybridRetriever(
    supermemory_api_key="your_key_here",
    faiss_weight=0.6,  # 60% weight for FAISS
    memory_weight=0.4  # 40% weight for Supermemory
)

# Get hybrid results with scores
results = retriever.retrieve_hybrid("Your query here", top_k=4)

# Get formatted context
context = retriever.retrieve_and_format_hybrid("Your query here")

# Get entity relationships from query
entities = retriever.get_entity_context("Your query here")

# Update memory after response
retriever.update_memory_with_response(
    user_query="What are the fees?",
    response="The B.Tech fees are..."
)
```

## How It Works

### Retrieval Flow

1. **Query Input**: User asks a question
2. **Parallel Retrieval**:
   - FAISS: Searches vector store using embeddings
   - Supermemory: Searches knowledge graph using entity relationships
3. **Scoring**: Results from both sources are scored
4. **Deduplication**: Duplicate results are removed
5. **Ranking**: Combined results are ranked by overall relevance
6. **Context Formation**: Top results formatted into context for LLM

### Scoring System

- **FAISS Score**: Cosine similarity (0-1) × FAISS weight (default 0.6)
- **Supermemory Score**: Entity match strength (0-1) × Memory weight (default 0.4)
- **Combined Score**: Sum of weighted scores

## Benefits

✨ **Enhanced Retrieval**
- Captures both semantic similarity and entity relationships
- Better handling of domain-specific relationships (e.g., "B.Tech" ↔ "fees")
- Tracks conversation context and relationships over time

🎯 **Improved Answers**
- More relevant context retrieved
- Better understanding of relationships between concepts
- Memory of previous interactions

⚙️ **Flexible Configuration**
- Adjust FAISS vs Supermemory weight based on your needs
- Works with or without API key (falls back to FAISS)
- Easy to add more documents to memory graph

## Troubleshooting

### Issue: "SUPERMEMORY_API_KEY not found"

**Solution**: Add your API key to `.env`:
```
SUPERMEMORY_API_KEY=your_key_here
```

### Issue: "Supermemory not installed"

**Solution**: Install the package:
```bash
pip install supermemory-py
```

### Issue: Hybrid mode not available

**Solution**: The system automatically falls back to FAISS if:
- API key is not set
- Supermemory library is not installed
- Memory graph initialization fails

Check the console output for details.

## Advanced: Tuning Weights

Adjust the retrieval balance based on your needs:

```python
# More emphasis on vector similarity
retriever = HybridRetriever(faiss_weight=0.75, memory_weight=0.25)

# More emphasis on entity relationships
retriever = HybridRetriever(faiss_weight=0.40, memory_weight=0.60)

# Equal weight
retriever = HybridRetriever(faiss_weight=0.50, memory_weight=0.50)
```

## Memory Management

The Supermemory memory graph automatically:
- Extracts entities and relationships from new documents
- Tracks conversation history
- Updates when new responses are generated

To manually add content to memory:

```python
from memory_graph import SupermemoryMemoryGraph

memory = SupermemoryMemoryGraph(api_key="your_key_here")

# Add document to memory
memory.add_to_memory(
    content="B.Tech fees are ₹2,50,000 per year",
    metadata={"source": "fees.pdf", "type": "tuition"}
)

# Get entity relationships
entities = memory.get_entity_relationships("B.Tech fees")
```

## Next Steps

1. ✅ Set `SUPERMEMORY_API_KEY` in `.env`
2. ✅ Install dependencies: `pip install -r requirements.txt`
3. ✅ Run the app: `streamlit run app.py`
4. ✅ Switch to "Hybrid" mode in the sidebar
5. ✅ Ask your questions and observe enhanced retrieval!

For more info, check the inline documentation in:
- `src/memory_graph.py` - Memory graph module
- `src/hybrid_retriever.py` - Hybrid retriever implementation
- `src/chatbot.py` - Updated chatbot with dual-mode support
