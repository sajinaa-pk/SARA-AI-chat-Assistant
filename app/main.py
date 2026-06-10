from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional
import uuid
from app.chat import stream_chat
from app.history import get_history, save_history, clear_history

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    use_wiki: bool = False

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("app/templates/index.html") as f:
        return HTMLResponse(content=f.read())

@app.post("/chat")
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    history = get_history(session_id)

    async def generate():
        full_response = ""
        for chunk in stream_chat(history, request.message, request.use_wiki):
            full_response += chunk
            yield chunk

        updated_history = history + [
            {"role": "user", "content": request.message},
            {"role": "assistant", "content": full_response}
        ]
        save_history(session_id, updated_history)

    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={"X-Session-ID": session_id}
    )

@app.delete("/chat/{session_id}")
async def clear_chat(session_id: str):
    clear_history(session_id)
    return {"message": "Chat history cleared"}

@app.get("/health")
async def health():
    return {"status": "ok"}