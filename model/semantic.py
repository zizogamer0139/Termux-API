from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class SemanticMeaning:
    subject: str
    relation: str
    object: str
    meaning_type: str
    confidence: float


class SemanticAnalyzer:

    SUBJECT_WORDS = {
        "i": "user",
        "me": "user",
        "my": "user",
        "mine": "user",
        "you": "assistant",
        "your": "assistant",
        "yours": "assistant",
    }

    PREFERENCE_RELATIONS = {
        "like": "likes",
        "love": "loves",
        "enjoy": "enjoys",
        "prefer": "prefers",
        "hate": "hates",
        "dislike": "dislikes",
        "want": "wants",
        "need": "needs",
    }

    COPULA_WORDS = {
        "am",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
    }

    def analyze(self, text: str) -> SemanticMeaning:

        original = text.strip()

        if not original:
            return SemanticMeaning(
                subject="",
                relation="",
                object="",
                meaning_type="empty",
                confidence=1.0,
            )

        cleaned = re.sub(
            r"[.!?,;:]+$",
            "",
            original,
        )

        words = cleaned.split()

        if not words:
            return SemanticMeaning(
                subject="",
                relation="",
                object="",
                meaning_type="empty",
                confidence=1.0,
            )

        subject = self._find_subject(words)

        preference = self._find_preference(words)

        if preference is not None:

            index, relation = preference

            object_text = " ".join(
                words[index + 1:]
            ).strip()

            if object_text:

                return SemanticMeaning(
                    subject=subject,
                    relation=relation,
                    object=object_text,
                    meaning_type="preference",
                    confidence=0.94,
                )

        copula = self._find_copula(words)

        if copula is not None:

            index, relation = copula

            object_text = " ".join(
                words[index + 1:]
            ).strip()

            if object_text:

                return SemanticMeaning(
                    subject=subject,
                    relation=relation,
                    object=object_text,
                    meaning_type="statement",
                    confidence=0.88,
                )

        return self._analyze_general_statement(
            words,
            subject,
        )

    def _find_subject(
        self,
        words: list[str],
    ) -> str:

        if not words:
            return ""

        first = words[0].lower()

        if first in self.SUBJECT_WORDS:
            return self.SUBJECT_WORDS[first]

        return words[0]

    def _find_preference(
        self,
        words: list[str],
    ) -> tuple[int, str] | None:

        for index, word in enumerate(words):

            normalized = word.lower()

            relation = self.PREFERENCE_RELATIONS.get(
                normalized
            )

            if relation is not None:
                return index, relation

        return None

    def _find_copula(
        self,
        words: list[str],
    ) -> tuple[int, str] | None:

        for index, word in enumerate(words):

            normalized = word.lower()

            if normalized in self.COPULA_WORDS:

                if normalized in {
                    "am",
                    "is",
                    "are",
                }:
                    return index, normalized

        return None

    def _analyze_general_statement(
        self,
        words: list[str],
        subject: str,
    ) -> SemanticMeaning:

        if len(words) >= 2:

            relation = words[1].lower()

            object_text = " ".join(
                words[2:]
            ).strip()

            if object_text:

                return SemanticMeaning(
                    subject=subject,
                    relation=relation,
                    object=object_text,
                    meaning_type="statement",
                    confidence=0.62,
                )

        return SemanticMeaning(
            subject=subject,
            relation="",
            object="",
            meaning_type="unknown",
            confidence=0.30,
        )


semantic_analyzer = SemanticAnalyzer()


def analyze_semantics(
    text: str,
) -> SemanticMeaning:

    return semantic_analyzer.analyze(text)