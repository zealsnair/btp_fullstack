from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from utils import load_pdf, split_text, index_docs, retrieve_docs, answer_question
import os

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    os.makedirs("uploaded_pdfs", exist_ok=True)
    file_path = os.path.join("uploaded_pdfs", file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    documents = load_pdf(file_path)
    if not documents:
        return {"success": False, "error": "Failed to extract text"}
    
    chunks = split_text(documents)
    if not chunks:
        return {"success": False, "error": "No valid chunks"}

    index_docs(chunks)
    return {"success": True, "message": "PDF processed and indexed"}

@app.post("/ask/")
async def ask_question(question: str = Form(...)):
    docs = retrieve_docs(question)
    if not docs:
        return {"answer": "I couldn't find relevant information."}
    answer = answer_question(question, docs)
    return {"answer": answer}
