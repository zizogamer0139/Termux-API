from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ParsedMessage:
    intent: str
    content: str
    confidence: float


class MessageParser:

    def parse(self, message: str) -> ParsedMessage:

        original = message.strip()
        text = original.lower()

        if not original:
            return ParsedMessage(
                intent="empty",
                content="",
                confidence=1.0
            )

        # --------------------------------------------------
        # GREETINGS
        # --------------------------------------------------

        greeting_patterns = [
            r"^hello\b",
            r"^hi\b",
            r"^hey\b",
            r"^yo\b",
            r"^good morning\b",
            r"^good afternoon\b",
            r"^good evening\b",
        ]

        if any(re.search(pattern, text) for pattern in greeting_patterns):
            return ParsedMessage(
                intent="greeting",
                content=original,
                confidence=0.99
            )

        # --------------------------------------------------
        # GOODBYE
        # --------------------------------------------------

        goodbye_patterns = [
            r"^goodbye\b",
            r"^bye\b",
            r"^see you\b",
            r"^see ya\b",
            r"^later\b",
        ]

        if any(re.search(pattern, text) for pattern in goodbye_patterns):
            return ParsedMessage(
                intent="goodbye",
                content=original,
                confidence=0.99
            )

        # --------------------------------------------------
        # IDENTITY
        # --------------------------------------------------

        identity_patterns = [
            r"who are you",
            r"what are you",
            r"what is your name",
            r"what's your name",
            r"tell me about yourself",
        ]

        if any(pattern in text for pattern in identity_patterns):
            return ParsedMessage(
                intent="identity",
                content=original,
                confidence=0.98
            )

        # --------------------------------------------------
        # HELP
        # --------------------------------------------------

        help_patterns = [
            r"^help$",
            r"help me",
            r"what can you do",
            r"how can you help",
            r"commands",
        ]

        if any(pattern in text for pattern in help_patterns):
            return ParsedMessage(
                intent="help",
                content=original,
                confidence=0.96
            )

        # --------------------------------------------------
        # MEMORY SAVE
        # --------------------------------------------------

        memory_save_patterns = [
            r"^remember that ",
            r"^remember ",
            r"^save that ",
            r"^save this ",
            r"^don't forget that ",
            r"^dont forget that ",
            r"^keep in mind that ",
        ]

        for pattern in memory_save_patterns:

            match = re.match(pattern, original, re.IGNORECASE)

            if match:

                content = original[match.end():].strip()

                return ParsedMessage(
                    intent="memory_save",
                    content=content,
                    confidence=0.99
                )

        # --------------------------------------------------
        # MEMORY FORGET
        # --------------------------------------------------

        memory_forget_patterns = [
            r"^forget that ",
            r"^forget ",
            r"^remove from memory ",
            r"^delete from memory ",
            r"^don't remember ",
            r"^dont remember ",
        ]

        for pattern in memory_forget_patterns:

            match = re.match(pattern, original, re.IGNORECASE)

            if match:

                content = original[match.end():].strip()

                return ParsedMessage(
                    intent="memory_forget",
                    content=content,
                    confidence=0.99
                )

        # --------------------------------------------------
        # TIME
        # --------------------------------------------------

        time_patterns = [
            "what time is it",
            "what's the time",
            "whats the time",
            "current time",
            "tell me the time",
            "time right now",
            "what time",
            "time now",
        ]

        if any(pattern in text for pattern in time_patterns):
            return ParsedMessage(
                intent="time",
                content=original,
                confidence=0.99
            )

        # --------------------------------------------------
        # DATE
        # --------------------------------------------------

        date_patterns = [
            "what is the date",
            "what's the date",
            "whats the date",
            "what date is it",
            "current date",
            "today's date",
            "todays date",
            "today's date",
            "what day is it",
            "what day is today",
            "today",
        ]

        if any(pattern in text for pattern in date_patterns):

            return ParsedMessage(
                intent="date",
                content=original,
                confidence=0.99
            )

        # --------------------------------------------------
        # WEB SEARCH
        # --------------------------------------------------

        search_patterns = [
            r"^search for ",
            r"^search ",
            r"^look up ",
            r"^look for ",
            r"^find information about ",
            r"^find info about ",
            r"^google ",
            r"^browse for ",
        ]

        for pattern in search_patterns:

            match = re.match(pattern, original, re.IGNORECASE)

            if match:

                query = original[match.end():].strip()

                return ParsedMessage(
                    intent="web_search",
                    content=query,
                    confidence=0.98
                )

        # --------------------------------------------------
        # COMMANDS
        # --------------------------------------------------

        command_patterns = [
            r"^open ",
            r"^launch ",
            r"^start ",
            r"^run ",
            r"^close ",
            r"^stop ",
            r"^install ",
            r"^uninstall ",
            r"^delete ",
            r"^create ",
        ]

        if any(re.match(pattern, text) for pattern in command_patterns):

            return ParsedMessage(
                intent="command",
                content=original,
                confidence=0.92
            )

        # --------------------------------------------------
        # CALCULATIONS
        # --------------------------------------------------

        # First check for a pure mathematical expression.
        #
        # Examples:
        # 25 * 4
        # 100 / 5
        # 10 + 20
        # (5 + 5) * 2
        # 2^10

        math_expression_pattern = re.compile(
            r"^[\d\s+\-*/%^().]+$"
        )

        if math_expression_pattern.fullmatch(original):

            return ParsedMessage(
                intent="calculation",
                content=original,
                confidence=0.99
            )

        # --------------------------------------------------
        # NATURAL LANGUAGE CALCULATIONS
        # --------------------------------------------------

        # Examples:
        # What is 25 * 4?
        # What's 100 / 5?
        # Calculate 50 + 20
        # Solve 12 * 12
        # How much is 10 + 15?

        calculation_patterns = [
            r"what is\s+(.+)",
            r"what's\s+(.+)",
            r"whats\s+(.+)",
            r"calculate\s+(.+)",
            r"solve\s+(.+)",
            r"compute\s+(.+)",
            r"how much is\s+(.+)",
        ]

        for pattern in calculation_patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:

                expression = match.group(1).strip()

                # Remove question marks and surrounding punctuation.
                expression = expression.rstrip("?!.")

                # Only classify as a calculation if the extracted
                # section actually contains numbers and math operators.

                if (
                    re.search(r"\d", expression)
                    and re.search(r"[+\-*/%^]", expression)
                ):

                    return ParsedMessage(
                        intent="calculation",
                        content=expression,
                        confidence=0.98
                    )

        # --------------------------------------------------
        # QUESTIONS
        # --------------------------------------------------

        question_patterns = [
            r"^what\b",
            r"^why\b",
            r"^how\b",
            r"^when\b",
            r"^where\b",
            r"^who\b",
            r"^which\b",
            r"^can\b",
            r"^could\b",
            r"^would\b",
            r"^is\b",
            r"^are\b",
            r"^do\b",
            r"^does\b",
            r"^did\b",
            r"\?$",
        ]

        if any(re.search(pattern, text) for pattern in question_patterns):

            return ParsedMessage(
                intent="question",
                content=original,
                confidence=0.90
            )

        # --------------------------------------------------
        # NORMAL CONVERSATION
        # --------------------------------------------------

        return ParsedMessage(
            intent="conversation",
            content=original,
            confidence=0.75
        )


# ----------------------------------------------------------
# GLOBAL PARSER
# ----------------------------------------------------------

parser = MessageParser()


def parse_message(message: str) -> ParsedMessage:
    return parser.parse(message)