from foundry_local_sdk import Configuration, FoundryLocalManager
import numpy as np
import sqlite3
import json
import os
import glob

def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def load_and_chunk_documents():
    all_chunks = []
    for filepath in glob.glob("*.txt"):
        filename = os.path.basename(filepath)
        if filename == "requirements.txt":  
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        for para in paragraphs:
            all_chunks.append({"source": filename, "content": para})
    return all_chunks

def setup_database():
    conn = sqlite3.connect("documents.db")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS documents")
    cursor.execute("""
        CREATE TABLE documents (
            id INTEGER PRIMARY KEY,
            source TEXT,
            content TEXT,
            embedding TEXT
        )
    """)
    conn.commit()
    return conn

def get_top_chunks(query, embed_client, k=3):
    conn = sqlite3.connect("documents.db")
    cursor = conn.cursor()
    cursor.execute("SELECT source, content, embedding FROM documents")
    rows = cursor.fetchall()
    conn.close()

    query_response = embed_client.generate_embedding(query)
    query_embedding = query_response.data[0].embedding

    scored_chunks = []
    for source, content, embedding_json in rows:
        chunk_embedding = json.loads(embedding_json)
        score = cosine_similarity(query_embedding, chunk_embedding)
        scored_chunks.append((score, source, content))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return scored_chunks[:k]

def answer_query(question, embed_client, chat_client, k=3):
    top_chunks = get_top_chunks(question, embed_client, k=k)

    context_text = "\n\n".join(
        f"[Source: {source}]\n{content}" for score, source, content in top_chunks
    )

    system_prompt = (
    "You are a question-answering assistant. Answer ONLY using the information below. "
    "Do not use any external or general knowledge.\n\n"
    "Decide first: does the information below FULLY answer the question?\n"
    "- If YES: give a clear, confident answer using only that information.\n"
    "- If NO: respond with exactly 'I don't have enough information on this topic.' "
    "and nothing else.\n"
    "Never mix both behaviors in the same answer.\n\n"
    f"INFORMATION:\n{context_text}"
)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]

    response = chat_client.complete_chat(messages,max_tokens=150)
    return response.choices[0].message.content

def main():
    config = Configuration(app_name="rag_assistant")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    embed_model = manager.catalog.get_model("qwen3-embedding-0.6b")
    embed_model.download()
    embed_model.load()
    embed_client = embed_model.get_embedding_client()

    chat_model = manager.catalog.get_model("phi-3.5-mini")
    chat_model.download()
    chat_model.load()
    chat_client = chat_model.get_chat_client()

    chunks = load_and_chunk_documents()
    print(f"Total {len(chunks)} chunks found.\n")

    texts = [c["content"] for c in chunks]
    batch_response = embed_client.generate_embeddings(texts)
    embeddings = [item.embedding for item in batch_response.data]

    conn = setup_database()
    cursor = conn.cursor()
    for chunk, emb in zip(chunks, embeddings):
        embedding_json = json.dumps(emb)
        cursor.execute(
            "INSERT INTO documents (source, content, embedding) VALUES (?, ?, ?)",
            (chunk["source"], chunk["content"], embedding_json)
        )
    conn.commit()
    conn.close()
    print("All chunks were converted to embedding and saved to SQLite.\n")

    print("--- Welcome to the RAG Assistant ---")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Your question: ")
        if question.strip().lower() == "exit":
            print("Goodbye!")
            break
        answer = answer_query(question, embed_client, chat_client)
        print(f"Answer: {answer}\n")

if __name__ == "__main__":
    main()