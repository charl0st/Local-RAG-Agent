import streamlit as st
import json
from foundry_local_sdk import Configuration, FoundryLocalManager
from main import (
    load_and_chunk_documents,
    setup_database,
    get_top_chunks,
    answer_query,
)

st.set_page_config(page_title="RAG Asistanı", page_icon="🤖")
st.title("Local RAG Agent")
st.write("Bu asistan, sadece kendi ders notu dokümanlarına dayanarak sorularını cevaplar. Tamamen offline çalışır.")


@st.cache_resource
def setup():
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

    return embed_client, chat_client, len(chunks)

with st.spinner("Modeller yükleniyor, ilk seferde biraz sürebilir..."):
    embed_client, chat_client, chunk_count = setup()

st.success(f"Sistem hazır, {chunk_count} tane chunk yüklendi.")


question = st.text_input("Sorunuzu yazın:")

if question:
    with st.spinner("Cevap hazırlanıyor..."):
        answer = answer_query(question, embed_client, chat_client)
    st.markdown("### Cevap:")
    st.write(answer)