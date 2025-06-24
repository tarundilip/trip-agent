import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "models/gemini-2.0-flash")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not set in environment variables.")

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel(MODEL_NAME)

def query_llm(prompt: str, context: str = "") -> str:
    try:
        response = model.generate_content([context, prompt] if context else prompt)
        return response.text.strip()
    except Exception as e:
        return f"LLM Error: {str(e)}"