import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash")


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to your .env file.")
    return genai.Client(api_key=api_key)


def ask_llm(prompt: str) -> str:
    """Send a prompt to Gemini and return the reply text."""
    client = get_client()
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text
