# AI Chat Assistant

A production-grade AI chat assistant built with FastAPI, Groq LLM, Redis, ChromaDB, and Docker. Features real-time streaming responses, persistent chat history, Wikipedia-powered answers, and a full RAG pipeline for chatting with your own PDF documents — complete with page-level citations and hallucination guardrails.

## Features

- **Streaming responses** — words appear in real time, like ChatGPT
- **Chat history** — Redis stores conversation context with 24hr auto-expiry
- **Session management** — multiple users, separate conversations
- **Wikipedia mode** — toggle on to get answers sourced from Wikipedia with citations
- **PDF RAG mode** — upload any PDF, ask questions, get answers grounded only in that document with page citations
- **Hallucination guardrails** — if the answer isn't in the source, the assistant says so instead of guessing
- **Clean UI** — minimal chat interface built into the app
- **Dockerized** — runs anywhere with one command

## Tech Stack

- **FastAPI** — backend framework
- **Groq** — LLM API (Llama 3.3 70B)
- **Redis** — chat history storage
- **ChromaDB** — vector store for document embeddings
- **pypdf** — PDF text extraction
- **Docker + Docker Compose** — containerization
- **Wikipedia API** — knowledge source for Wikipedia mode

## Project Structure

```
ai-chat-assistant/
│
├── app/
│   ├── main.py        # FastAPI routes, PDF upload endpoint
│   ├── chat.py        # Groq LLM streaming logic, mode routing
│   ├── history.py     # Redis chat history
│   ├── prompts.py     # Prompt templates (default, wiki, PDF)
│   ├── wiki.py         # Wikipedia search
│   ├── pdf_rag.py     # PDF extraction, chunking, embeddings, retrieval
│   └── templates/
│       └── index.html # Chat UI with PDF upload and Wikipedia toggle
│
├── .env               # API keys (never commit)
├── requirements.txt
├── docker-compose.yml
└── Dockerfile
```

## How the RAG Pipeline Works

**Indexing a PDF (runs once per upload):**

1. Extract text from each page using `pypdf`
2. Split text into overlapping chunks (500 words, 50-word overlap) so context isn't lost at chunk boundaries
3. Generate embeddings for each chunk
4. Store chunks + embeddings + page numbers in a ChromaDB collection

**Answering a question:**

1. Embed the user's question using the same embedding function
2. Run a similarity search against the document's ChromaDB collection (top-3 chunks by cosine similarity)
3. Inject the retrieved chunks into the prompt with explicit instructions: answer only from this context, cite the page number, and say so honestly if the answer isn't there
4. Stream the grounded answer back to the user

This last instruction is what prevents hallucination — the model is constrained to the retrieved context instead of falling back on its training data.

## Getting Started

### Prerequisites

- Docker installed
- Groq API key — get one free at [console.groq.com](https://console.groq.com)

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/ai-chat-assistant.git
cd ai-chat-assistant
```

### 2. Add your API key

Create a `.env` file in the root:

```
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run with Docker

```bash
docker compose up --build
```

### 4. Open the app

Go to [http://localhost:8000](http://localhost:8000)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Chat UI |
| POST | `/chat` | Send a message (supports `use_wiki` and `doc_id` flags) |
| POST | `/upload-pdf` | Upload and index a PDF, returns a `doc_id` |
| DELETE | `/chat/{session_id}` | Clear chat history |
| GET | `/health` | Health check |

### Example: basic chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hello, who are you?"}'
```

### Example: Wikipedia mode

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "what is machine learning?", "use_wiki": true}'
```

### Example: PDF upload

```bash
curl -X POST http://localhost:8000/upload-pdf \
  -F "file=@/path/to/document.pdf"
```

### Example: PDF-grounded question

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "what does this document say about X?", "doc_id": "the-doc-id-from-upload"}'
```

### Continue a conversation

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "tell me more", "session_id": "your-session-id"}'
```

## Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Redis
docker compose up -d redis

# Start the app with auto-reload
uvicorn app.main:app --reload
```

## Design Decisions

**Why Groq?**
Groq provides extremely fast inference on open source models like Llama 3.3. Free tier is generous enough for development and personal use.

**Why Redis for chat history?**
Chat history needs to be read and written on every single request. Redis provides sub-millisecond read/write speeds. Built-in TTL means old sessions auto-expire without a cleanup job.

**Why streaming?**
Streaming responses feel instant to the user. Without streaming, the user stares at a blank screen until the full response is ready — which can take 5-10 seconds for longer answers.

**Why ChromaDB for the vector store?**
Simple local-first API, no separate infrastructure to manage, and it's the fastest way to learn the actual mechanics of embeddings and similarity search before reaching for something like Pinecone or Weaviate in production.

**Why chunk with overlap?**
A hard cutoff at 500 words can split a sentence or idea in half, losing context right at the boundary. A 50-word overlap means each chunk carries a bit of the previous one's context forward.

**Why explicit "don't make things up" instructions in the PDF prompt?**
LLMs default to answering from training knowledge even when given context that doesn't contain the answer. An explicit instruction to stay within the provided excerpts — and to say so when it can't — is what actually reduces hallucination in practice, not just in theory.

**Why separate files?**
Each file has one responsibility — routing, LLM logic, history management, prompts, retrieval. This makes the code easy to test, modify, and explain in interviews.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Your Groq API key |
| `REDIS_HOST` | Redis host (default: `redis` in Docker, `localhost` locally) |
| `REDIS_PORT` | Redis port (default: `6379`) |

## License

MIT