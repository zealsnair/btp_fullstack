import streamlit as st
import os
import pinecone
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import cohere

# Load environment variables
load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not COHERE_API_KEY or not PINECONE_API_KEY:
    st.error("Missing API keys! Check your .env file.")
    st.stop()

co = cohere.Client(COHERE_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "pdf-index"
embedding_dim = 1024  # Must match embedding model

# Initialize Pinecone index

index = pc.Index(index_name)
# index.delete(delete_all=True)

# if index_name not in [index["name"] for index in pc.list_indexes()]:
# pc.create_index(
#     name=index_name,
#     dimension=embedding_dim,
#     metric="cosine",
#     # namespace="pdf-namespace",
#     spec=ServerlessSpec(cloud="aws", region="us-east-1")
# )
def get_embeddings(texts):
    embeddings = pc.inference.embed(
        model="llama-text-embed-v2",
        inputs=texts,
        parameters={"input_type": "passage", "truncate": "END"}
    )
    return embeddings

def load_pdf(file_path):
    loader = PDFPlumberLoader(file_path)
    return loader.load()

def split_text(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return text_splitter.split_documents(documents)

def index_docs(documents):
    texts = [doc.page_content for doc in documents]
    embeddings = get_embeddings(texts)
    vectors = []
    for i, (text, emb) in enumerate(zip(texts, embeddings)):
        if "values" not in emb:
            continue
        vectors.append({"id": str(i), "values": emb["values"], "metadata": {"text": text}})
    if vectors:
        index.upsert(vectors=vectors, namespace="pdf-namespace")

def retrieve_docs(query):
    embedding = get_embeddings([query])[0]
    results = index.query(
        vector=embedding.values,
        namespace="pdf-namespace",
        top_k=5,
        include_metadata=True
    )
    return [match["metadata"]["text"] for match in results.get("matches", [])]

def answer_question(question, retrieved_docs):
    context = "\n\n".join(retrieved_docs)
    prompt = f"""
    You are an assistant for question-answering tasks. Use the following retrieved context to answer detailed in points.
    \nQuestion: {question}\nContext: {context}\n\nAnswer:
    """
    response = co.generate(model="command-r-plus", prompt=prompt, temperature=0.3)
    return response.generations[0].text.strip()

st.title("Chat with Your PDF using Cohere & Pinecone 📄🤖")
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:
    file_path = os.path.join("uploaded_pdfs", uploaded_file.name)
    os.makedirs("uploaded_pdfs", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    documents = load_pdf(file_path)
    if documents:
        chunked_documents = split_text(documents)
        if chunked_documents:
            index_docs(chunked_documents)
            st.success("PDF processed and indexed successfully!")
        else:
            st.error("No valid text extracted from PDF.")
            st.stop()
    else:
        st.error("Failed to extract text from PDF.")
        st.stop()
    
    question = st.text_input("Ask a question about the PDF:")
    if question:
        related_docs = retrieve_docs(question)
        if related_docs:
            answer = answer_question(question, related_docs)
            st.write("### Answer:")
            st.write(answer)
        else:
            st.write("I couldn't find relevant information.")
