from app.services.gemini_provider import GeminiProvider
from app.services.deepseek_provider import DeepSeekProvider
from app.services.groq_provider import GroqProvider
from app.services.cerebras_provider import CerebrasProvider
from app.services.aionlabs_provider import AionLabsProvider


class AIRouter:
    def __init__(self):
        self.providers = [
            GeminiProvider(),
            DeepSeekProvider(),
            GroqProvider(),
            CerebrasProvider(),
            AionLabsProvider(),
        ]

    def generate(self, prompt):
        errors = []

        for provider in self.providers:
            if not provider.available:
                continue

            try:
                return provider.generate(prompt)

            except Exception as exc:
                errors.append(
                    f"{provider.name}: {type(exc).__name__}"
                )
                continue

        raise RuntimeError(
            "هیچ AI providerای در دسترس نیست"
        )