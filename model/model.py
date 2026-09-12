from __future__ import annotations

from .parser import parse_message
from .reasoning import reasoning_engine
from .response import response_engine


class TermuxAI:

    def __init__(self):

        self.name = "Termux AI"
        self.version = "0.1.0"

    def ask(
        self,
        message: str,
    ) -> str:

        parsed = parse_message(
            message
        )

        result = reasoning_engine.reason(
            parsed
        )

        return response_engine.generate(
            result
        )

    def process(
        self,
        message: str,
    ) -> dict:

        parsed = parse_message(
            message
        )

        result = reasoning_engine.reason(
            parsed
        )

        result["parsed"] = {
            "intent": parsed.intent,
            "content": parsed.content,
            "confidence": parsed.confidence,
        }

        return result


ai = TermuxAI()