from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()
client = OpenAI()

def evaluate_story(story: str, request: str) -> dict:
    """Judge a story against rubric and return JSON feedback."""
    judge_prompt = Path("prompts/judge_prompt.txt").read_text(encoding="utf-8")

    messages = [
        {"role": "system", "content": judge_prompt},
        {"role": "user", "content": f"Request: {request}\n\nStory:\n{story}"},
    ]

    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    raw = resp.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON from judge", "raw": raw}
