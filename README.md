# SARA AI Chat Assistant

A production-grade AI chat assistant built with FastAPI, Groq LLM, Redis, and Docker. Features real-time streaming responses, persistent chat history, and Wikipedia-powered answers.

## Features

- **Streaming responses** — words appear in real time, like ChatGPT
- **Chat history** — Redis stores conversation context with 24hr auto-expiry
- **Session management** — multiple users, separate conversations
- **Wikipedia mode** — toggle on to get answers sourced from Wikipedia with citations
- **Clean UI** — minimal chat interface built into the app
- **Dockerized** — runs anywhere with one command

## Tech Stack

- **FastAPI** — backend framework
- **Groq** — LLM API (Llama 3.3 70B)
- **Redis** — chat history storage
- **Docker + Docker Compose** — containerization
- **Wikipedia API** — knowledge source for Wikipedia mode

## Project Structure

```
ai-chat-assistant/
│
├── app/
│   ├── main.py        # FastAPI routes
│   ├── chat.py        # Groq LLM streaming logic
│   ├── history.py     # Redis chat history
│   ├── prompts.py     # Prompt templates
│   ├── wiki.py        # Wikipedia search
│   └── templates/
│       └── index.html # Chat UI
│
├── .env               # API keys (never commit)
├── requirements.txt
├── docker-compose.yml
└── Dockerfile
```

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
| POST | `/chat` | Send a message |
| DELETE | `/chat/{session_id}` | Clear chat history |
| GET | `/health` | Health check |

### Example request

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hello, who are you?"}'
```

### With Wikipedia mode

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "what is machine learning?", "use_wiki": true}'
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

**Why separate files?**
Each file has one responsibility — routing, LLM logic, history management, prompts. This makes the code easy to test, modify, and explain in interviews.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Your Groq API key |
| `REDIS_HOST` | Redis host (default: `redis` in Docker, `localhost` locally) |
| `REDIS_PORT` | Redis port (default: `6379`) |

## License

MIT