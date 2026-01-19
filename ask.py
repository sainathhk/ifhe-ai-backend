import os
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from vector_store import query_documents
from google import genai

# ------------------ Router ------------------
router = APIRouter()

# ------------------ Gemini Client ------------------
# IMPORTANT: Set GEMINI_API_KEY in environment variable
# Windows: setx GEMINI_API_KEY "AIzaSy..."
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# ------------------ Request Schema ------------------
class Question(BaseModel):
    question: str

# ------------------ Gemini Helper (Retry-safe) ------------------
def call_gemini_with_retry(prompt: str, retries: int = 3, delay: int = 2):
    last_error = None

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            if response and response.text:
                return response.text.strip()

            return None

        except Exception as e:
            last_error = str(e)

            # Retry ONLY when model is overloaded
            if "503" in last_error or "UNAVAILABLE" in last_error:
                time.sleep(delay * (attempt + 1))
                continue
            else:
                break

    raise HTTPException(
        status_code=500,
        detail=f"Gemini failed after retries: {last_error}"
    )

# ------------------ Ask Endpoint ------------------
@router.post("/ask")
def ask_question(data: Question):
    try:
        # 1️⃣ Search IFHE documents (Vector DB)
        docs = query_documents(data.question)

        # 2️⃣ IFHE DOCUMENT-BASED ANSWER
        if docs:
            context = "\n".join(docs)

            prompt = f"""
You are an IFHE academic assistant.
Answer ONLY using the context below.
If the answer is not present, say "NOT_FOUND".

Context:
{context}

Question:
{data.question}
"""
            answer = call_gemini_with_retry(prompt)

            if answer and "NOT_FOUND" not in answer:
                return {
                    "answer": answer,
                    "source": "ifhe_documents"
                }

        # 3️⃣ GENERAL QUESTION (Fallback)
        general_prompt = f"""
You are a helpful AI assistant.
Answer the following question clearly and concisely.

Question:
{data.question}
"""
        general_answer = call_gemini_with_retry(general_prompt)

        if general_answer:
            return {
                "answer": general_answer,
                "source": "general_ai"
            }

        # 4️⃣ Model busy (very rare after retries)
        return {
            "answer": "The AI model is currently busy. Please try again shortly."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
