import re

from app.services.ai_router import AIRouter


class DocumentAIService:
    def __init__(self):
        self.router = AIRouter()

    def summarize(self, chunks, language="en"):
        if not chunks:
            raise ValueError("هیچ متنی برای خلاصه‌سازی وجود ندارد")

        language_instruction = self._summary_language_instruction(
            language
        )

        summaries = []

        for index, chunk in enumerate(chunks, start=1):
            prompt = f"""
You are summarizing a document.

IMPORTANT RULES:
- Use ONLY information explicitly stated in the document section.
- Do NOT add outside knowledge.
- Do NOT guess or infer facts that are not explicitly stated.
- Do NOT add explanations that are not present in the document.
- If a name, date, fact, or claim is not present in the text, do not mention it.
- Preserve the meaning of the original text.
- {language_instruction}

Document section {index}:

{chunk}
"""

            summary = self.router.generate(prompt)
            summaries.append(summary)

        final_prompt = f"""
You are creating the final summary of a document.

IMPORTANT RULES:
- Use ONLY the information contained in the section summaries below.
- Do NOT add outside knowledge.
- Do NOT introduce new facts.
- Do NOT correct, expand, or supplement the information using your own knowledge.
- Preserve the important ideas and relationships.
- {language_instruction}

Section summaries:

{chr(10).join(summaries)}
"""

        return self.router.generate(final_prompt)

    def answer_question(
        self,
        question,
        chunks,
        max_chunks=5,
        language="en",
    ):
        if not question or not question.strip():
            raise ValueError("سؤال الزامی است")

        if not chunks:
            raise ValueError("هیچ متنی برای پاسخ‌گویی وجود ندارد")

        language_instruction = self._answer_language_instruction(
            language
        )

        relevant_chunks = self._find_relevant_chunks(
            question,
            chunks,
            max_chunks=max_chunks,
        )

        context = "\n\n".join(relevant_chunks)

        prompt = f"""
You are answering a question about a document.

IMPORTANT RULES:
- Answer ONLY from the provided document context.
- Do NOT use outside knowledge.
- Do NOT guess.
- Do NOT add facts that are not explicitly present in the context.
- If the answer is not available in the context, say that the
  information is not available in the provided document.
- {language_instruction}

Question:
{question}

Document context:
{context}
"""

        return self.router.generate(prompt)

    @staticmethod
    def _summary_language_instruction(language):
        if language == "fa":
            return (
                "Write the summary entirely in Persian (Farsi). "
                "Translate the meaning naturally, but do not add "
                "any information that is not present in the source."
            )

        if language == "en":
            return (
                "Write the summary entirely in English. "
                "Do not add any information that is not present "
                "in the source."
            )

        raise ValueError("زبان باید fa یا en باشد")

    @staticmethod
    def _answer_language_instruction(language):
        if language == "fa":
            return (
                "Answer entirely in Persian (Farsi). "
                "Translate the answer naturally, but do not add "
                "any information that is not present in the document."
            )

        if language == "en":
            return (
                "Answer entirely in English. "
                "Do not add any information that is not present "
                "in the document."
            )

        raise ValueError("زبان باید fa یا en باشد")

    def _find_relevant_chunks(self, question, chunks, max_chunks=5):
        question_words = self._keywords(question)

        scored_chunks = []

        for index, chunk in enumerate(chunks):
            chunk_words = self._keywords(chunk)

            score = len(
                question_words.intersection(chunk_words)
            )

            scored_chunks.append(
                (score, index, chunk)
            )

        scored_chunks.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        selected = [
            chunk
            for score, index, chunk in scored_chunks[:max_chunks]
            if score > 0
        ]

        if not selected:
            return chunks[:max_chunks]

        return selected

    @staticmethod
    def _keywords(text):
        words = re.findall(
            r"\b[\w]+\b",
            text.lower(),
            flags=re.UNICODE,
        )

        stop_words = {
            # English
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "what",
            "who",
            "where",
            "when",
            "why",
            "how",
            "and",
            "or",
            "of",
            "to",
            "in",
            "for",
            "on",
            "with",
            "this",
            "that",
            "it",
            "be",
            "as",
            "by",
            "from",

            # Persian
            "و",
            "یا",
            "از",
            "به",
            "در",
            "با",
            "برای",
            "که",
            "این",
            "آن",
            "را",
            "است",
            "هست",
            "بود",
            "شد",
            "چه",
            "کی",
            "کجا",
            "چرا",
            "چگونه",
            "یک",
        }

        return {
            word
            for word in words
            if word not in stop_words
        }