import os

from dotenv import load_dotenv
from groq import Groq

from app.services.ai_provider import AIProvider


load_dotenv()


class GroqProvider(AIProvider):
    name = "groq"

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        self.available = bool(api_key)
        self.client = None

        if self.available:
            self.client = Groq(api_key=api_key)

    def generate(self, prompt):
        if not self.available:
            raise RuntimeError("Groq provider is not configured")

        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError("Groq returned an empty response")

        return content