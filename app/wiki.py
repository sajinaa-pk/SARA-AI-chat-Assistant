import wikipediaapi

wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent='AI-Chat-Assistant/1.0'
)

def search_wikipedia(query: str) -> dict:
    page = wiki.page(query)
    
    if not page.exists():
        return None
    
    # Get first 3000 characters — enough context, not too many tokens
    content = page.summary[:3000]
    
    return {
        "title": page.title,
        "content": content,
        "url": page.fullurl
    }