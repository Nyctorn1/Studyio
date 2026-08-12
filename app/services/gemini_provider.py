import os

from dotenv import load_dotenv
from google import genai

from app.services.ai_provider import AIProvider


load_dotenv()


class GeminiProvider(AIProvider):
    name = "gemini"

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        self.available = bool(api_key)
        self.client = None

        if self.available:
            self.client = genai.Client(api_key=api_key)

    def generate(self, prompt):
        if not self.available:
            raise RuntimeError("Gemini provider is not configured")

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response")

        return response.text