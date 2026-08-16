import re

from app.services.ai_router import AIRouter


class DocumentAIService:
    """
    مرحله‌ای برای خلاصه‌سازی و پرسش‌وپاسخ اسناد بزرگ.

    هدف اصلی:
    - کاهش هزینه و تعداد requestهای AI
    - جلوگیری از ارسال batchهای بیش از حد بزرگ
    - فشرده‌سازی تدریجی سند
    - رسیدن به خلاصه نهایی حدود 20٪ اندازه متن اصلی
    - پاسخ‌گویی به سؤال بر اساس بخش‌های مرتبط سند
    """

    # =========================================================
    # SUMMARY CONFIG
    # =========================================================

    MAX_CHARS_PER_BATCH = 12000

    FINAL_SUMMARY_RATIO = 0.20

    MAX_CHARS_PER_REDUCTION_BATCH = 16000

    # =========================================================
    # INIT
    # =========================================================

    def __init__(self):
        self.router = AIRouter()

    # =========================================================
    # SUMMARY
    # =========================================================

    def summarize(self, chunks, language="en"):
        if not chunks:
            raise ValueError(
                "هیچ متنی برای خلاصه‌سازی وجود ندارد"
            )

        language_instruction = (
            self._summary_language_instruction(language)
        )

        source_text = "\n".join(chunks)
        source_chars = len(source_text)

        target_chars = max(
            1000,
            int(
                source_chars
                * self.FINAL_SUMMARY_RATIO
            ),
        )

        batches = self._build_batches(
            chunks,
            max_chars=self.MAX_CHARS_PER_BATCH,
        )

        print(
            f"[DOCUMENT AI] Source chars: {source_chars}"
        )

        print(
            f"[DOCUMENT AI] Target summary chars: "
            f"{target_chars}"
        )

        print(
            f"[DOCUMENT AI] Initial batches: "
            f"{len(batches)}"
        )

        batch_summaries = []

        for batch_number, batch in enumerate(
            batches,
            start=1,
        ):
            print(
                f"[DOCUMENT AI] Processing batch "
                f"{batch_number}/{len(batches)}"
            )

            prompt = self._build_batch_summary_prompt(
                batch=batch,
                batch_number=batch_number,
                target_chars=target_chars,
                language_instruction=language_instruction,
            )

            summary = self.router.generate(prompt)

            if summary and summary.strip():
                batch_summaries.append(
                    summary.strip()
                )

        if not batch_summaries:
            raise RuntimeError(
                "هیچ خلاصه‌ای از سند تولید نشد"
            )

        if len(batch_summaries) == 1:
            final_summary = batch_summaries[0]

            if len(final_summary) > target_chars * 1.25:
                print(
                    "[DOCUMENT AI] Final summary is above "
                    "target size; running final compression"
                )

                prompt = self._build_final_compression_prompt(
                    summary=final_summary,
                    target_chars=target_chars,
                    language_instruction=language_instruction,
                )

                final_summary = self.router.generate(
                    prompt
                )

            return final_summary.strip()

        # =====================================================
        # REDUCTION
        # =====================================================

        current_summaries = batch_summaries
        reduction_round = 1

        while len(current_summaries) > 1:

            reduction_batches = self._build_text_batches(
                current_summaries,
                max_chars=(
                    self.MAX_CHARS_PER_REDUCTION_BATCH
                ),
            )

            print(
                f"[DOCUMENT AI] Reduction round "
                f"{reduction_round}: "
                f"{len(current_summaries)} summaries -> "
                f"{len(reduction_batches)} batches"
            )

            reduced_summaries = []

            for batch_number, group in enumerate(
                reduction_batches,
                start=1,
            ):
                print(
                    f"[DOCUMENT AI] Reduction batch "
                    f"{batch_number}/{len(reduction_batches)}"
                )

                prompt = self._build_reduction_prompt(
                    summaries=group,
                    target_chars=target_chars,
                    language_instruction=language_instruction,
                )

                reduced = self.router.generate(prompt)

                if reduced and reduced.strip():
                    reduced_summaries.append(
                        reduced.strip()
                    )

            if not reduced_summaries:
                raise RuntimeError(
                    "Reduction خلاصه‌ها شکست خورد"
                )

            current_summaries = reduced_summaries
            reduction_round += 1

        final_summary = current_summaries[0]

        # =====================================================
        # FINAL COMPRESSION
        # =====================================================

        if len(final_summary) > target_chars * 1.25:

            print(
                "[DOCUMENT AI] Final summary is above "
                "target size; running final compression"
            )

            prompt = self._build_final_compression_prompt(
                summary=final_summary,
                target_chars=target_chars,
                language_instruction=language_instruction,
            )

            final_summary = self.router.generate(
                prompt
            )

        return final_summary.strip()

    # =========================================================
    # BATCH BUILDING
    # =========================================================

    @staticmethod
    def _build_batches(
        chunks,
        max_chars,
    ):
        """
        چند chunk را تا زمانی که از max_chars عبور نکرده‌اند
        در یک batch قرار می‌دهد.

        یک chunk بزرگ به تنهایی هم اجازه ورود دارد.
        """

        batches = []
        current_batch = []
        current_chars = 0

        for chunk in chunks:

            if not chunk or not chunk.strip():
                continue

            chunk_chars = len(chunk)

            if (
                current_batch
                and current_chars + chunk_chars
                > max_chars
            ):
                batches.append(current_batch)

                current_batch = []
                current_chars = 0

            current_batch.append(chunk)
            current_chars += chunk_chars

        if current_batch:
            batches.append(current_batch)

        return batches

    @staticmethod
    def _build_text_batches(
        texts,
        max_chars,
    ):
        """
        برای intermediate summaryها batch می‌سازد.
        """

        batches = []
        current_batch = []
        current_chars = 0

        for text in texts:

            if not text or not text.strip():
                continue

            text_chars = len(text)

            if (
                current_batch
                and current_chars + text_chars
                > max_chars
            ):
                batches.append(current_batch)

                current_batch = []
                current_chars = 0

            current_batch.append(text)
            current_chars += text_chars

        if current_batch:
            batches.append(current_batch)

        return batches

    # =========================================================
    # BATCH SUMMARY PROMPT
    # =========================================================

    @staticmethod
    def _build_batch_summary_prompt(
        batch,
        batch_number,
        target_chars,
        language_instruction,
    ):
        sections = []

        for index, chunk in enumerate(
            batch,
            start=1,
        ):
            sections.append(
                f"""
--- Document section {index} ---

{chunk}
"""
            )

        document_text = "\n".join(sections)

        return f"""
You are summarizing part of a larger document.

This is batch {batch_number}.

IMPORTANT RULES:

- Use ONLY information explicitly stated in the document sections.
- Do NOT use outside knowledge.
- Do NOT guess.
- Do NOT infer facts that are not explicitly stated.
- Do NOT invent names, dates, claims, or details.
- Preserve important facts and relationships.
- Preserve important definitions, arguments, conclusions,
  evidence, dates, names, and technical concepts.
- Remove repetition.
- Combine related information.
- Remove low-value details and unnecessary examples.
- Do not add commentary about the summarization process.
- {language_instruction}

The final document summary is intended to be approximately
20% of the original document length.

This is an intermediate summary.

Preserve the information that will be important when creating
the final document summary.

Prefer dense factual compression over verbose explanation.

Do not intentionally force this batch to be exactly
{target_chars} characters. Focus on preserving important
information while remaining substantially shorter than
the source.

Document sections:

{document_text}

Now produce ONE concise intermediate summary.
"""

    # =========================================================
    # REDUCTION PROMPT
    # =========================================================

    @staticmethod
    def _build_reduction_prompt(
        summaries,
        target_chars,
        language_instruction,
    ):
        joined = []

        for index, summary in enumerate(
            summaries,
            start=1,
        ):
            joined.append(
                f"""
--- Intermediate summary {index} ---

{summary}
"""
            )

        summaries_text = "\n".join(joined)

        return f"""
You are compressing multiple intermediate summaries
into one more concise summary.

IMPORTANT RULES:

- Use ONLY information contained in the summaries below.
- Do NOT add outside knowledge.
- Do NOT introduce new facts.
- Do NOT guess or infer missing information.
- Preserve important facts, names, dates, claims,
  relationships, arguments, evidence, and conclusions.
- Preserve important definitions and technical concepts.
- Remove repetition.
- Merge related points.
- Remove low-value details.
- Prefer concise factual statements.
- Do not add commentary about the summarization process.
- {language_instruction}

The desired final summary size is approximately
{target_chars} characters.

Do not try to preserve every sentence.

Preserve the most important information and relationships.

Intermediate summaries:

{summaries_text}

Create ONE substantially shorter combined summary.
"""

    # =========================================================
    # FINAL COMPRESSION
    # =========================================================

    @staticmethod
    def _build_final_compression_prompt(
        summary,
        target_chars,
        language_instruction,
    ):
        return f"""
You are performing the final compression of a document summary.

IMPORTANT RULES:

- Use ONLY information contained in the provided summary.
- Do NOT add outside knowledge.
- Do NOT invent facts.
- Do NOT guess.
- Preserve the most important facts, arguments,
  definitions, names, dates, relationships, evidence,
  and conclusions.
- Preserve important technical concepts.
- Remove repetition and low-value details.
- Prefer dense factual writing.
- Do not add commentary about the summarization process.
- {language_instruction}

Target length:

approximately {target_chars} characters.

Current summary:

{summary}

Rewrite this summary into a substantially shorter,
information-dense final summary.
"""

    # =========================================================
    # QUESTION ANSWERING
    # =========================================================

    def answer_question(
        self,
        question,
        chunks,
        max_chunks=8,
        language="en",
    ):
        if not question or not question.strip():
            raise ValueError(
                "سؤال الزامی است"
            )

        if not chunks:
            raise ValueError(
                "هیچ متنی برای پاسخ‌گویی وجود ندارد"
            )

        language_instruction = (
            self._answer_language_instruction(language)
        )

        relevant_chunks = self._find_relevant_chunks(
            question,
            chunks,
            max_chunks=max_chunks,
        )

        context_sections = []

        for index, chunk in relevant_chunks:
            context_sections.append(
                f"""
--- Document section {index + 1} ---

{chunk}
"""
            )

        context = "\n".join(
            context_sections
        )

        prompt = f"""
You are answering a question about a document.

Your job is to answer the user's question using ONLY
the provided document sections.

IMPORTANT RULES:

- Use ONLY information explicitly present in the document.
- Do NOT use outside knowledge.
- Do NOT guess.
- Do NOT hallucinate.
- Do NOT add facts that are not explicitly present.
- If the document does not contain enough information
  to answer the question, clearly say that the information
  is not available in the provided document.
- If the document contains only partial information,
  answer only what can be supported by the document.
- Preserve important names, dates, concepts, arguments,
  evidence, relationships, and conclusions.
- When possible, explain the answer using the terminology
  and concepts used by the document.
- Do not mention the retrieval process.
- Do not mention "chunks" or "document sections"
  in your answer unless necessary.
- Answer directly.
- {language_instruction}

Question:

{question}

Relevant document sections:

{context}

Now answer the question directly and accurately.
"""

        return self.router.generate(prompt)

    # =========================================================
    # LANGUAGE
    # =========================================================

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

        raise ValueError(
            "زبان باید fa یا en باشد"
        )

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

        raise ValueError(
            "زبان باید fa یا en باشد"
        )

    # =========================================================
    # RELEVANCE
    # =========================================================

    def _find_relevant_chunks(
        self,
        question,
        chunks,
        max_chunks=8,
    ):
        if not chunks:
            return []

        question_words = self._keywords(
            question
        )

        if not question_words:
            return [
                (index, chunk)
                for index, chunk
                in enumerate(
                    chunks[:max_chunks]
                )
            ]

        scored_chunks = []

        for index, chunk in enumerate(chunks):

            chunk_words = self._keywords(
                chunk
            )

            if not chunk_words:
                continue

            overlap = question_words.intersection(
                chunk_words
            )

            score = len(overlap)

            if score > 0:
                scored_chunks.append(
                    (
                        score,
                        index,
                        chunk,
                    )
                )

        # relevance بیشتر اول
        # و در صورت مساوی بودن، ترتیب سند.
        scored_chunks.sort(
            key=lambda item: (
                -item[0],
                item[1],
            )
        )

        selected = scored_chunks[:max_chunks]

        if not selected:
            return [
                (index, chunk)
                for index, chunk
                in enumerate(
                    chunks[:max_chunks]
                )
            ]

        # بعد از relevance ranking،
        # ترتیب واقعی سند را حفظ می‌کنیم.
        selected.sort(
            key=lambda item: item[1]
        )

        return [
            (
                index,
                chunk,
            )
            for score, index, chunk
            in selected
        ]

    # =========================================================
    # KEYWORDS
    # =========================================================

    @staticmethod
    def _keywords(text):
        """
        استخراج keyword برای retrieval.

        این مرحله:
        - lowercase می‌کند
        - نیم‌فاصله را normalize می‌کند
        - حروف عربی/فارسی را normalize می‌کند
        - punctuation را حذف می‌کند
        - stop wordهای فارسی و انگلیسی را حذف می‌کند
        - چند پسوند ساده را برای matching بهتر حذف می‌کند.

        این هنوز semantic search نیست؛
        فقط keyword retrieval قوی‌تر است.
        """

        if not text:
            return set()

        # -----------------------------------------------------
        # Normalize text
        # -----------------------------------------------------

        text = text.lower()

        # normalize Persian/Arabic characters
        text = (
            text
            .replace("ي", "ی")
            .replace("ى", "ی")
            .replace("ك", "ک")
            .replace("ۀ", "ه")
            .replace("ة", "ه")
        )

        # normalize zero-width characters
        text = (
            text
            .replace("\u200c", " ")
            .replace("\u200d", " ")
            .replace("\ufeff", " ")
        )

        # -----------------------------------------------------
        # Tokenize
        # -----------------------------------------------------

        words = re.findall(
            r"[a-zA-Zآ-یء]+",
            text,
            flags=re.UNICODE,
        )

        stop_words = {
            # =================================================
            # English
            # =================================================

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
            "about",
            "which",
            "does",
            "do",
            "did",
            "has",
            "have",
            "had",
            "can",
            "could",
            "would",
            "should",
            "will",
            "there",
            "their",
            "they",
            "them",
            "these",
            "those",
            "into",
            "than",
            "then",
            "also",
            "not",
            "only",
            "but",
            "its",
            "been",
            "being",

            # =================================================
            # Persian
            # =================================================

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
            "های",
            "ها",
            "هم",
            "نیز",
            "اما",
            "اگر",
            "تا",
            "بر",
            "درباره",
            "مورد",
            "آنها",
            "اینها",
            "شود",
            "می",
            "کرد",
            "کرده",
            "خواهد",
            "هستند",
            "بودند",
            "دارد",
            "دارند",
            "داشت",
            "داشتند",
            "کنند",
            "کند",
            "کردند",
            "شده",
            "شوند",
            "شدند",
            "استفاده",
        }

        keywords = set()

        for word in words:

            if not word:
                continue

            if word in stop_words:
                continue

            # -------------------------------------------------
            # Persian suffix normalization
            # -------------------------------------------------

            # جمع
            if word.endswith("های"):
                word = word[:-3]

            elif word.endswith("ها"):
                word = word[:-2]

            # comparative
            elif word.endswith("ترین"):
                word = word[:-4]

            elif word.endswith("تر"):
                word = word[:-2]

            # -------------------------------------------------
            # English suffix normalization
            # -------------------------------------------------

            if len(word) > 4:

                if word.endswith("ing"):
                    word = word[:-3]

                elif word.endswith("ed"):
                    word = word[:-2]

                elif word.endswith("es"):
                    word = word[:-2]

                elif word.endswith("s"):
                    word = word[:-1]

            if len(word) >= 2:
                keywords.add(word)

        return keywords