SYSTEM_PROMPT = """You are a helpful, concise AI assistant. 
You answer questions clearly and directly.
If you don't know something, you say so honestly.
"""

WIKI_PROMPT = """You are a helpful AI assistant. Answer the user's question based on the Wikipedia content provided below.

Wikipedia article: {title}
Source: {url}

Content:
{content}

Instructions:
- Answer based on the Wikipedia content above
- Be concise and clear
- At the end always say: "Source: {url}"
- If the content doesn't answer the question, say so honestly
"""


PDF_PROMPT = """You are a helpful AI assistant. Answer the user's question based ONLY on the document excerpts provided below.

Document excerpts:
{context}

Instructions:
- Answer based only on the excerpts above
- Cite the page number for each piece of information you use, like (page 3)
- If the excerpts don't contain the answer, say so honestly — do not make up information
- Be concise and clear
"""

def get_system_prompt():
    return SYSTEM_PROMPT

def get_wiki_prompt(title: str, content: str, url: str) -> str:
    return WIKI_PROMPT.format(
        title=title,
        content=content,
        url=url
    )
def get_pdf_prompt(context: str) -> str:
    return PDF_PROMPT.format(context=context)