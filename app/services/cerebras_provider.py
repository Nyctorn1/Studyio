import os

from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

from app.services.ai_provider import AIProvider


load_dotenv()


class CerebrasProvider(AIProvider):
    name = "cerebras"

    def __init__(self):
        api_key = os.getenv("CEREBRAS_API_KEY")

        self.available = bool(api_key)
        self.client = None

        if self.available:
            self.client = Cerebras(api_key=api_key)

    def generate(self, prompt):
        if not self.available:
            raise RuntimeError("Cerebras provider is not configured")

        response = self.client.chat.completions.create(
            model="llama-3.1-8b",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError("Cerebras returned an empty response")

        return content