import os

from dotenv import load_dotenv
from openai import OpenAI

from app.services.ai_provider import AIProvider


load_dotenv()


class DeepSeekProvider(AIProvider):
    name = "deepseek"

    def __init__(self):
        api_key = os.getenv("DEEPSEEK_API_KEY")

        self.available = bool(api_key)
        self.client = None

        if self.available:
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com",
            )

    def generate(self, prompt):
        if not self.available:
            raise RuntimeError("DeepSeek provider is not configured")

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError("DeepSeek returned an empty response")

        return content