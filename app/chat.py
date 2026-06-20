from groq import Groq
import os
from dotenv import load_dotenv
from app.prompts import get_system_prompt, get_wiki_prompt, get_pdf_prompt
from app.wiki import search_wikipedia
from app.pdf_rag import search_pdf

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def build_messages(history: list, user_message: str, wiki_context: dict = None, pdf_context: str = None) -> list:
    if pdf_context:
        system = get_pdf_prompt(context=pdf_context)
    elif wiki_context:
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

def stream_chat(history: list, user_message: str, use_wiki: bool = False, doc_id: str = None):
    wiki_context = None
    pdf_context = None

    if doc_id:
        chunks = search_pdf(doc_id, user_message)
        pdf_context = "\n\n".join(
            [f"[Page {c['page']}]\n{c['text']}" for c in chunks]
        )
    elif use_wiki:
        wiki_context = search_wikipedia(user_message)

    messages = build_messages(history, user_message, wiki_context, pdf_context)

    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        stream=True
    )
    for chunk in stream:
        text = chunk.choices[0].delta.content
        if text:
            yield text