from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

def revise_story(story: str, feedback: dict, request: str) -> str:
    """Revise story using feedback from judge."""
    suggestions = "\n".join(feedback.get("suggestions", [])) or "Tighten clarity and ensure a calm ending."

    messages = [
        {"role": "system", "content": "You are a careful story reviser."},
        {"role": "user", "content": f"Original request: {request}"},
        {"role": "assistant", "content": story},
        {"role": "user", "content": f"Please revise the story based on these suggestions:\n{suggestions}"},
    ]

    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    return resp.choices[0].message.content.strip()
