import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader
import os

chroma_client = chromadb.PersistentClient(path="./chroma_data")

embedding_fn = embedding_functions.DefaultEmbeddingFunction()

def get_or_create_collection(doc_id: str):
    return chroma_client.get_or_create_collection(
        name=f"doc_{doc_id}",
        embedding_function=embedding_fn
    )
#reads the PDF page by page, keeps track of which text came from which page
def extract_text_from_pdf(file_path: str) -> list:
    reader = PdfReader(file_path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text.strip():
            pages.append({"page": i + 1, "text": text})
    return pages
#splits text into chunks of 500 words, with 50-word overlap between chunks. The overlap prevents losing context that spans a chunk boundary
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks
#runs the full pipeline: extract → chunk → store in ChromaDB with page numbers attached
def index_pdf(file_path: str, doc_id: str):
    collection = get_or_create_collection(doc_id)
    pages = extract_text_from_pdf(file_path)

    documents = []
    metadatas = []
    ids = []
    counter = 0

    for page_data in pages:
        page_num = page_data["page"]
        text = page_data["text"]
        chunks = chunk_text(text)

        for chunk in chunks:
            documents.append(chunk)
            metadatas.append({"page": page_num})
            ids.append(f"{doc_id}_chunk_{counter}")
            counter += 1

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    return len(documents)
 #takes a question, embeds it automatically (ChromaDB's embedding_function handles this), and returns the top 3 most similar chunks with their page numbers
def search_pdf(doc_id: str, query: str, top_k: int = 3) -> list:
    collection = get_or_create_collection(doc_id)
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "page": results["metadatas"][0][i]["page"]
        })

    return chunks