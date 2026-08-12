from app.services.chunking import chunk_text


def prepare_document(text):
    chunks = chunk_text(text)

    return {
        "chunks": chunks,
        "chunk_count": len(chunks),
        "characters": len(text)
    }