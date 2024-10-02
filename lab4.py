import streamlit as st
from openai import OpenAI

_import_("pysqlite3")
import sys

sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
import chromadb
from chromadb.utils import embedding_functions
import PyPDF2

client = OpenAI(api_key=st.secrets["openai_key"])


def create_collection(pdfs):
    if "db" not in st.session_state:
        st.session_state.db = chromadb.PersistentClient().get_or_create_collection(
            "HW4_collection"
        )
        embedder = embedding_functions.OpenAIEmbeddingFunction(
            api_key=st.secrets["openai_key"], model_name="text-embedding-3-small"
        )

        for pdf in pdfs:
            try:
                text = "".join(
                    [page.extract_text() for page in PyPDF2.PdfReader(pdf).pages]
                )
                st.session_state.db.add(
                    documents=[text], metadatas=[{"filename": pdf.name}], ids=[pdf.name]
                )
            except Exception as e:
                st.error(f"Error processing {pdf.name}: {e}")
        st.success("Collection created!")


def get_context(query):
    if "db" in st.session_state:
        results = st.session_state.db.query(
            query_texts=[query], n_results=5, include=["documents", "metadatas"]
        )
        return "".join(
            [
                f"From '{meta['filename']}':\n{doc}\n\n"
                for doc, meta in zip(results["documents"][0], results["metadatas"][0])
            ]
        )
    return ""


def generate_response(messages):
    try:
        return (
            client.chat.completions.create(
                model="gpt-4o-mini", messages=messages, max_tokens=200
            )
            .choices[0]
            .message.content
        )
    except Exception as e:
        return f"Error: {str(e)}"


st.title("Course Information Chatbot")
pdf_files = st.file_uploader(
    "Upload PDF files", accept_multiple_files=True, type=["pdf"]
)
if st.button("Create Collection") and pdf_files:
    create_collection(pdf_files)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("What would you like to know?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    context = get_context(prompt)
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant for course questions.",
        },
        {"role": "user", "content": f"Context: {context}\n\nQuestion: {prompt}"},
    ]

    response = generate_response(messages)
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
