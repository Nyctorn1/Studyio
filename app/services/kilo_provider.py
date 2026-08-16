import os

from openai import OpenAI

from app.services.ai_provider import AIProvider


class KiloProvider(AIProvider):
    name = "Kilo"

    def __init__(self):
        api_key = os.getenv("KILO_API_KEY")

        self.available = bool(api_key)

        self.client = None

        if self.available:
            self.client = OpenAI(
                base_url="https://api.kilo.ai/api/openrouter",
                api_key=api_key,
            )

    def generate(self, prompt):
        if not self.available or self.client is None:
            raise RuntimeError(
                "Kilo API key is not configured"
            )

        response = self.client.chat.completions.create(
            model=os.getenv(
                "KILO_MODEL",
                "openrouter/free",
            ),
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content