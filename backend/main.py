from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import requests
import numpy as np
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "api.env"))
NEW_API_KEY = os.getenv("NEW_API_KEY")
print("DEBUG: Using OpenRouter API key:", NEW_API_KEY is not None)

# FastAPI setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/
ROOT_DIR = os.path.dirname(BASE_DIR)                   # project root
KB_PATH = os.path.join(ROOT_DIR, "data", "kb.json")    
EMBED_PATH = os.path.join(ROOT_DIR, "kb_embeddings.npy")
QUESTIONS_PATH = os.path.join(ROOT_DIR, "kb_questions.json")



# Load knowledge base
try:
    with open(KB_PATH, "r", encoding="utf-8") as f:
        kb = json.load(f)
    print(f"DEBUG: Loaded KB with {len(kb)} entries")
except FileNotFoundError:
    kb = []
    print("⚠️ KB not found, kb.json missing!")

# Request model structure
class Question(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"message": "Backend is working!"}

# Initialize embedding model
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def load_or_create_embeddings():
    """Load embeddings from file if they match KB; otherwise, create and save them."""
    if not kb:
        print("Knowledge base is empty.")
        return []

    kb_questions = [item.get("question", "") for item in kb if "question" in item]

    if os.path.exists(QUESTIONS_PATH) and os.path.exists(EMBED_PATH):
        try:
            with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
                stored_questions = json.load(f)
            if stored_questions == kb_questions:
                print("Loading cached embeddings...")
                return np.load(EMBED_PATH)
            else:
                print("KB changed — regenerating embeddings...")
        except Exception as e:
            print("Error loading cached embeddings:", e)

    print("Computing embeddings for KB...")
    embeddings = embedding_model.encode(kb_questions, convert_to_numpy=True)

    np.save(EMBED_PATH, embeddings)
    with open(QUESTIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(kb_questions, f, ensure_ascii=False, indent=2)

    print("Embeddings saved successfully.")
    return embeddings

kb_embeddings = load_or_create_embeddings()

def normalize_text(text: str):
    """Normalize text for semantic search."""
    return re.sub(r"[^\w\s]", "", text.lower().strip())

def find_kb_answer(user_question: str):
    """
    First tries to find an exact match in the KB.
    If no exact match, performs semantic search as fallback.
    """
    # 1️⃣ Exact match check
    for item in kb:
        if item.get("question", "").strip().lower() == user_question.lower():
            print("DEBUG: Exact KB match found")
            return item["answer"]

    # 2️⃣ Semantic search fallback
    if not kb or len(kb_embeddings) == 0:
        return None

    user_question_norm = normalize_text(user_question)
    query_embedding = embedding_model.encode(user_question_norm, convert_to_numpy=True)
    similarities = util.cos_sim(query_embedding, kb_embeddings)[0]

    best_idx = int(np.argmax(similarities))
    best_score = float(similarities[best_idx])

    print(f"DEBUG: Semantic match score: {best_score:.3f}, question: {kb[best_idx]['question']}")
    
    # Only return semantic answer if similarity is reasonably high
    if best_score >= 0.6:
        return kb[best_idx]["answer"]

    # No KB answer found
    return None

@app.post("/ask")
def ask_question(question: Question):
    user_question = question.question.strip()

    # Check KB first
    kb_answer = find_kb_answer(user_question)
    if kb_answer:
        return {"answer": kb_answer}

    # Fallback to OpenRouter API
    if not NEW_API_KEY:
        return {"answer": "API key not found."}

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {NEW_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are an intelligent AI assistant that helps users with their questions regarding the university. Answer clearly and politely.",
            },
            {"role": "user", "content": user_question}
        ],
        "stream": False
    }

    try:
        print("DEBUG: Sending request to OpenRouter...")
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        answer = data.get("choices", [{}])[0].get("message", {}).get("content", "No answer returned.")
        return {"answer": answer.strip()}
    except requests.exceptions.RequestException as e:
        print("⚠️ OpenRouter request failed:", e)
        return {"answer": f"⚠️ API request error: {e}"}

# Run backend
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
