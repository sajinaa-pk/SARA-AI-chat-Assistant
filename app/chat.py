from groq import Groq
import os
from dotenv import load_dotenv
from app.prompts import get_system_prompt, get_wiki_prompt
from app.wiki import search_wikipedia

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def build_messages(history: list, user_message: str, wiki_context: dict = None) -> list:
    if wiki_context:
        system = get_wiki_prompt(
            title=wiki_context["title"],
            content=wiki_context["content"],
            url=wiki_context["url"]
        )
    else:
        system = get_system_prompt()

    messages = [{"role": "system", "content": system}]

    for msg in history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    messages.append({"role": "user", "content": user_message})
    return messages

def stream_chat(history: list, user_message: str, use_wiki: bool = False):
    wiki_context = None

    if use_wiki:
        wiki_context = search_wikipedia(user_message)

    messages = build_messages(history, user_message, wiki_context)

    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        stream=True
    )
    for chunk in stream:
        text = chunk.choices[0].delta.content
        if text:
            yield text