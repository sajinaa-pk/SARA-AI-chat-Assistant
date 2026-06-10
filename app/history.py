import redis
import json
import os

redis_client = redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379"),
    decode_responses=True
)

def get_history(session_id: str) -> list:
    history = redis_client.get(f"chat:{session_id}")
    if history:
        return json.loads(history)
    return []

def save_history(session_id: str, messages: list):
    redis_client.setex(
        f"chat:{session_id}",
        86400,
        json.dumps(messages)
    )

def clear_history(session_id: str):
    redis_client.delete(f"chat:{session_id}")