from app.services.kilo_provider import KiloProvider
from app.services.gemini_provider import GeminiProvider
from app.services.groq_provider import GroqProvider
from app.services.cerebras_provider import CerebrasProvider
from app.services.aionlabs_provider import AionLabsProvider
from app.services.gapgpt_provider import GapGPTProvider


class AIRouter:
    def __init__(self):
        self.providers = [
            GeminiProvider(),
            KiloProvider(),
            GroqProvider(),
            CerebrasProvider(),
            GapGPTProvider(),
            AionLabsProvider(),
        ]

        # Providers that permanently failed during this router's lifetime.
        self.disabled_providers = set()

    def generate(self, prompt):
        errors = []

        for provider in self.providers:
            if not provider.available:
                continue

            if provider.name in self.disabled_providers:
                print(
                    f"[AI ROUTER] Skipping disabled provider: "
                    f"{provider.name}"
                )
                continue

            print(f"[AI ROUTER] Trying provider: {provider.name}")

            try:
                result = provider.generate(prompt)

                print(f"[AI ROUTER] SUCCESS: {provider.name}")

                return result

            except Exception as exc:
                print(
                    f"[AI ROUTER] FAILED: "
                    f"{provider.name} -> "
                    f"{type(exc).__name__}: {exc}"
                )

                errors.append(
                    f"{provider.name}: {type(exc).__name__}"
                )

                if self._is_permanent_error(exc):
                    self.disabled_providers.add(provider.name)

                    print(
                        f"[AI ROUTER] DISABLED provider: "
                        f"{provider.name}"
                    )

        raise RuntimeError(
            "AI provider در دسترس نیست"
        )

    @staticmethod
    def _is_permanent_error(exc):
        message = str(exc).lower()

        permanent_markers = (
            "401",
            "402",
            "403",
            "404",
            "invalid api key",
            "invalid_api_key",
            "insufficient balance",
            "insufficient_balance",
            "permission denied",
            "forbidden",
            "not found",
            "model not found",
        )

        return any(
            marker in message
            for marker in permanent_markers
        )