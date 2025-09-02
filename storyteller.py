from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()  # reads OPENAI_API_KEY from .env
client = OpenAI()  # picks up OPENAI_API_KEY from env

def generate_story(request: str) -> str:
    """Generate a story draft using the storyteller prompt."""
    storyteller_prompt = Path("prompts/storyteller_prompt.txt").read_text(encoding="utf-8")

    messages = [
        {"role": "system", "content": storyteller_prompt},
        {"role": "user", "content": request},
    ]

    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    return resp.choices[0].message.content.strip()
