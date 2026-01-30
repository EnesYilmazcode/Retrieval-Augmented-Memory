import streamlit as st
import google.generativeai as genai
import chromadb
import os
import uuid
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash-lite")

# chromadb setup - stores chat history as vectors
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("chat_memory")

def store_message(role, content):
    collection.add(
        documents=[content],
        metadatas=[{"role": role}],
        ids=[str(uuid.uuid4())]
    )

def get_relevant_context(query, k=5):
    if collection.count() == 0:
        return ""

    results = collection.query(query_texts=[query], n_results=min(k, collection.count()))

    if not results["documents"][0]:
        return ""

    # format the retrieved messages
    context_lines = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        prefix = "User" if meta["role"] == "user" else "Assistant"
        context_lines.append(f"{prefix}: {doc}")

    return "\n".join(context_lines)

# ui
st.title("RAG Memory Chat")

if st.button("Clear Memory"):
    chroma_client.delete_collection("chat_memory")
    chroma_client.get_or_create_collection("chat_memory")
    st.session_state.messages = []
    st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Message"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # get relevant past messages instead of sending everything
    context = get_relevant_context(prompt, k=5)

    if context:
        full_prompt = f"Context:\n{context}\n\nUser: {prompt}"
    else:
        full_prompt = prompt

    response = model.generate_content(full_prompt)
    reply = response.text

    # save to memory
    store_message("user", prompt)
    store_message("assistant", reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)
