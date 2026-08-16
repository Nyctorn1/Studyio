import os

from openai import OpenAI

from app.services.ai_provider import AIProvider


class GapGPTProvider(AIProvider):
    name = "GapGPT"

    def __init__(self):
        api_key = os.getenv("GAPGPT_API_KEY")

        self.available = bool(api_key)

        self.client = None

        if self.available:
            self.client = OpenAI(
                base_url="https://api.gapgpt.app/v1",
                api_key=api_key,
            )

    def generate(self, prompt):
        if not self.available or self.client is None:
            raise RuntimeError(
                "GapGPT API key is not configured"
            )

        response = self.client.chat.completions.create(
            model=os.getenv(
                "GAPGPT_MODEL",
                "gpt-4o",
            ),
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        content = response.choices[0].message.content

        print(
            "[GapGPT] RESPONSE:",
            repr(content),
        )

        if not content or not content.strip():
            raise RuntimeError(
                "GapGPT returned an empty response"
            )

        return content