def chunk_text(pages, chunk_size=800, overlap=150):
    chunks = []

    for page in pages:
        text = page["text"]

        start = 0

        while start < len(text):
            end = start + chunk_size

            chunk = text[start:end].strip()

            if chunk:
                chunks.append({
                    "text": chunk,
                    "source": page["source"],
                    "page": page["page"]
                })

            if end >= len(text):
                break

            start = end - overlap

    return chunks