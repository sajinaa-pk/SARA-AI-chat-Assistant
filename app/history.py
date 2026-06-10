import redis
import json
import os

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

# fetches previous messages for a user session from Redis
def get_history(session_id: str) -> list:
    history = redis_client.get(f"chat:{session_id}")
    if history:
        return json.loads(history)
    return []
#saves updated messages back to Redis, auto-expires after 24 hours
def save_history(session_id: str, messages: list):
    redis_client.setex(
        f"chat:{session_id}",
        86400,  # expires after 24 hours
        json.dumps(messages)
    )
#wipes a session, like a "new chat" button
def clear_history(session_id: str):
    redis_client.delete(f"chat:{session_id}")# unique ID per user, like user_123. This is how we separate conversations