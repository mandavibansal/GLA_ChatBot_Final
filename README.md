# GLA Admission Chatbot

A Retrieval-Augmented Generation (RAG) chatbot for GLA University admission information.
This project uses Groq, LangChain, FAISS, and PDF brochure ingestion to answer questions from GLA documents.

## Contributors

- Mandavi Bansal
- Devanshi Bansal
- Saumya Singh

## Features

- Ingests PDF brochures from `data/`
- Extracts text using OCR
- Converts text into searchable embeddings
- Uses FAISS vector search for fast retrieval
- Answers admission-related queries through a Groq-powered LLM

## Setup

1. Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy the environment template and add your API key:

```bash
cp .env.example .env
```

4. Open `.env` and set your Groq API key:

```text
GROQ_API_KEY=your_api_key_here
```

## Usage

1. Place GLA brochure PDFs into the `data/` directory.
2. Build the vector store by running:

```bash
python3 scripts/ingest.py
```

3. Start the Streamlit app:

```bash
streamlit run app.py
```

4. Open the local URL shown in the terminal to chat with the bot.

## Project Structure

- `app.py` — Streamlit application UI
- `scripts/ingest.py` — PDF ingestion and vector store creation
- `src/ocr_loader.py` — PDF text extraction
- `src/chunker.py` — Text chunking
- `src/embedder.py` — Embedding generation
- `src/retriever.py` — Vector retrieval logic
- `src/groq_llm.py` — Groq API integration
- `src/chatbot.py` — Chatbot orchestration
- `requirements.txt` — Python dependencies

## Notes

- Do not commit `.env` or `vector_store/` to Git.
- If the vector store is missing, rerun `python3 scripts/ingest.py`.
- For OCR issues, install Tesseract:
  - macOS: `brew install tesseract`
  - Ubuntu: `sudo apt install tesseract-ocr`
