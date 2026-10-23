import re
from collections import Counter
from app.services.document_processor import chunk_text

def retrieve_relevant(text: str, query: str, limit: int = 4) -> list[str]:
    chunks=chunk_text(text)
    terms=set(re.findall(r"[a-zA-Z0-9]{3,}", query.lower()))
    scored=[]
    for chunk in chunks:
        words=re.findall(r"[a-zA-Z0-9]{3,}", chunk.lower())
        counts=Counter(words)
        score=sum(min(counts[t], 4) for t in terms)
        if score: scored.append((score, chunk))
    scored.sort(key=lambda x:x[0], reverse=True)
    return [c for _,c in scored[:limit]] or chunks[:min(limit, len(chunks))]
