from __future__ import annotations

import ast
import operator
import re
from datetime import datetime

from .knowledge import knowledge
from .memory import memory
from .semantic import analyze_semantics
from .web import search_web


class SafeCalculator:

    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def calculate(self, expression: str) -> str:

        expression = expression.strip()

        try:
            tree = ast.parse(
                expression,
                mode="eval"
            )

            result = self._evaluate(tree.body)

            if isinstance(result, float) and result.is_integer():
                return str(int(result))

            return str(result)

        except Exception:
            return "I couldn't calculate that."

    def _evaluate(self, node):

        if isinstance(node, ast.Constant):

            if isinstance(node.value, (int, float)):
                return node.value

            raise ValueError("Invalid constant.")

        if isinstance(node, ast.BinOp):

            operation = self.OPERATORS.get(
                type(node.op)
            )

            if operation is None:
                raise ValueError("Unsupported operator.")

            left = self._evaluate(node.left)
            right = self._evaluate(node.right)

            return operation(left, right)

        if isinstance(node, ast.UnaryOp):

            operation = self.OPERATORS.get(
                type(node.op)
            )

            if operation is None:
                raise ValueError("Unsupported operator.")

            return operation(
                self._evaluate(node.operand)
            )

        raise ValueError("Unsupported expression.")


class AnswerBuilder:

    STOP_WORDS = {
        "what",
        "is",
        "are",
        "the",
        "a",
        "an",
        "why",
        "how",
        "does",
        "do",
        "can",
        "could",
        "would",
        "should",
        "tell",
        "me",
        "about",
        "explain",
        "please",
        "you",
        "your",
        "and",
        "or",
        "to",
        "of",
        "in",
        "on",
        "for",
        "with",
        "that",
        "this",
        "it",
        "be",
    }

    def _words(self, text: str) -> list[str]:

        return re.findall(
            r"[a-zA-Z0-9]+",
            text.lower()
        )

    def _important_words(self, text: str) -> list[str]:

        words = self._words(text)

        return [
            word
            for word in words
            if word not in self.STOP_WORDS
            and len(word) >= 3
        ]

    def _find_subject(
        self,
        question: str
    ) -> str:

        words = self._important_words(
            question
        )

        if not words:
            return ""

        known = []

        for entry in knowledge.entries:

            topic_words = self._important_words(
                entry.topic
            )

            keyword_words = []

            for keyword in entry.keywords:
                keyword_words.extend(
                    self._important_words(keyword)
                )

            for word in words:

                if word in topic_words:
                    known.append(
                        entry.topic
                    )
                    break

                if word in keyword_words:
                    known.append(
                        entry.topic
                    )
                    break

        if known:
            return known[0]

        return " ".join(words)

    def _select_knowledge(
        self,
        question: str
    ):

        return knowledge.search(
            question
        )

    def _select_memories(
        self,
        question: str
    ) -> list[dict]:

        question_words = set(
            self._important_words(question)
        )

        if not question_words:
            return []

        matches = []

        for item in memory.get_all():

            memory_words = set(
                self._important_words(
                    item["content"]
                )
            )

            overlap = (
                question_words
                & memory_words
            )

            if overlap:
                matches.append(
                    (
                        len(overlap),
                        item
                    )
                )

        matches.sort(
            key=lambda value: value[0],
            reverse=True
        )

        return [
            item
            for _, item in matches[:5]
        ]

    @staticmethod
    def _clean_snippet(
        snippet: str
    ) -> str:

        snippet = re.sub(
            r"\s+",
            " ",
            snippet
        )

        return snippet.strip()

    def _web_information(
        self,
        question: str
    ) -> list:

        return search_web(
            question,
            max_results=5
        )

    def _build_from_knowledge(
        self,
        question: str,
        entries
    ) -> str:

        if not entries:
            return ""

        subject = self._find_subject(
            question
        )

        facts = []

        for entry in entries:

            content = entry.content.strip()

            if content and content not in facts:
                facts.append(content)

        if not facts:
            return ""

        question_lower = question.lower()

        if (
            question_lower.startswith("why ")
            or "why " in question_lower
        ):

            return (
                f"Based on what I know about {subject}, "
                f"the relevant information is: "
                + " ".join(facts)
            )

        if (
            question_lower.startswith("how ")
            or "how does" in question_lower
            or "how do" in question_lower
        ):

            return (
                f"Here's what I can determine about "
                f"{subject}: "
                + " ".join(facts)
            )

        return " ".join(facts)

    def _build_from_web(
        self,
        question: str,
        results
    ) -> str:

        if not results:
            return ""

        subject = self._find_subject(
            question
        )

        pieces = []

        for result in results:

            title = result.title.strip()

            snippet = self._clean_snippet(
                result.snippet
            )

            if snippet:

                pieces.append(
                    f"{title}: {snippet}"
                )

            elif title:

                pieces.append(
                    title
                )

        if not pieces:
            return ""

        return (
            f"I found information related to "
            f"{subject}. "
            + " ".join(pieces[:3])
        )

    def _combine_information(
        self,
        knowledge_text: str,
        memories: list[dict],
        web_results: list
    ) -> str:

        sections = []

        if knowledge_text:

            sections.append(
                knowledge_text
            )

        if memories:

            memory_text = " ".join(
                item["content"].strip()
                for item in memories
                if item.get("content")
            )

            if memory_text:

                sections.append(
                    f"Relevant memory: {memory_text}"
                )

        if web_results:

            web_text = self._build_from_web(
                "",
                web_results
            )

            if web_text:

                sections.append(
                    web_text
                )

        return " ".join(sections)

    def generate(
        self,
        question: str,
        use_web: bool = False,
    ) -> str:

        entries = self._select_knowledge(
            question
        )

        memories = self._select_memories(
            question
        )

        knowledge_text = (
            self._build_from_knowledge(
                question,
                entries
            )
        )

        web_results = []

        if use_web:

            web_results = self._web_information(
                question
            )

        answer = self._combine_information(
            knowledge_text,
            memories,
            web_results
        )

        if answer:
            return answer

        return (
            "I don't have enough information to "
            "construct an answer yet."
        )


class SemanticResponseBuilder:

    def build(self, text: str) -> str:

        meaning = analyze_semantics(
            text
        )

        if meaning.meaning_type == "preference":

            return self._preference(
                meaning.relation,
                meaning.object
            )

        if meaning.meaning_type == "statement":

            return self._statement(
                meaning.subject,
                meaning.relation,
                meaning.object
            )

        return (
            "I understand what you're saying, "
            "but I need more information to reason "
            "about it."
        )

    @staticmethod
    def _preference(
        relation: str,
        object_text: str
    ) -> str:

        if relation == "likes":

            return (
                f"I understand that you like "
                f"{object_text}."
            )

        if relation == "loves":

            return (
                f"I understand that you love "
                f"{object_text}."
            )

        if relation == "enjoys":

            return (
                f"I understand that you enjoy "
                f"{object_text}."
            )

        if relation == "prefers":

            return (
                f"I understand that you prefer "
                f"{object_text}."
            )

        if relation == "hates":

            return (
                f"I understand that you hate "
                f"{object_text}."
            )

        if relation == "dislikes":

            return (
                f"I understand that you dislike "
                f"{object_text}."
            )

        if relation == "wants":

            return (
                f"I understand that you want "
                f"{object_text}."
            )

        if relation == "needs":

            return (
                f"I understand that you need "
                f"{object_text}."
            )

        return (
            f"I understand that you {relation} "
            f"{object_text}."
        )

    @staticmethod
    def _statement(
        subject: str,
        relation: str,
        object_text: str
    ) -> str:

        display_subject = subject

        if subject == "user":
            display_subject = "You"

        elif subject == "assistant":
            display_subject = "I"

        if relation in {
            "am",
            "is",
            "are",
        }:

            if display_subject == "You":

                return (
                    f"You are {object_text}."
                )

            if display_subject == "I":

                return (
                    f"I am {object_text}."
                )

        return (
            f"{display_subject} {relation} "
            f"{object_text}."
        )


class ReasoningEngine:

    def __init__(self):

        self.calculator = SafeCalculator()

        self.answer_builder = AnswerBuilder()

        self.semantic_response_builder = (
            SemanticResponseBuilder()
        )

    def reason(
        self,
        message
    ) -> dict:

        intent = message.intent
        content = message.content

        if intent == "empty":

            return {
                "response": "Please say something.",
                "action": "conversation",
            }

        if intent == "greeting":

            return {
                "response": (
                    "Hello! I'm Termux AI. 🤖"
                ),
                "action": "conversation",
            }

        if intent == "goodbye":

            return {
                "response": "Goodbye! 👋",
                "action": "conversation",
            }

        if intent == "identity":

            return {
                "response": (
                    "I'm Termux AI, a custom AI system "
                    "with my own reasoning engine."
                ),
                "action": "conversation",
            }

        if intent == "help":

            return {
                "response": (
                    "I can understand questions, "
                    "calculate expressions, search my "
                    "knowledge, use memory, search the "
                    "web, and construct answers from "
                    "retrieved information."
                ),
                "action": "help",
            }

        if intent == "calculation":

            result = self.calculator.calculate(
                content
            )

            return {
                "response": result,
                "action": "calculation",
            }

        if intent == "time":

            now = datetime.now().astimezone()

            return {
                "response": (
                    "The current local time is "
                    f"{now.strftime('%I:%M:%S %p')}."
                ),
                "action": "time",
            }

        if intent == "date":

            now = datetime.now().astimezone()

            date_text = "{} {}, {}".format(
                now.strftime("%B"),
                now.day,
                now.year
            )

            return {
                "response": (
                    "Today's date is {}.".format(
                        date_text
                    )
                ),
                "action": "date",
            }

        if intent == "memory_save":

            if not content:

                return {
                    "response": (
                        "I need something to remember."
                    ),
                    "action": "memory_save",
                }

            memory.save(content)

            return {
                "response": "I'll remember that.",
                "action": "memory_save",
            }

        if intent == "memory_forget":

            if not content:

                return {
                    "response": (
                        "I need to know what to forget."
                    ),
                    "action": "memory_forget",
                }

            deleted = memory.delete_matching(
                content
            )

            return {
                "response": (
                    f"I forgot {deleted} "
                    f"matching memory."
                    if deleted == 1
                    else
                    f"I forgot {deleted} "
                    f"matching memories."
                ),
                "action": "memory_forget",
            }

        if intent == "web_search":

            results = search_web(
                content,
                max_results=5
            )

            if not results:

                return {
                    "response": (
                        f"I couldn't find any web "
                        f"results for '{content}'."
                    ),
                    "action": "web_search",
                }

            lines = [
                f"Web results for: {content}",
                ""
            ]

            for index, result in enumerate(
                results,
                start=1
            ):

                lines.append(
                    f"{index}. {result.title}"
                )

                if result.snippet:

                    lines.append(
                        f"   {result.snippet}"
                    )

                lines.append(
                    f"   {result.url}"
                )

                lines.append("")

            return {
                "response": "\n".join(
                    lines
                ).strip(),
                "action": "web_search",
                "query": content,
                "results": results,
            }

        if intent == "question":

            entries = self._select_question_sources(
                content
            )

            memories = (
                self.answer_builder._select_memories(
                    content
                )
            )

            use_web = (
                not entries
                and not memories
            )

            answer = self.answer_builder.generate(
                content,
                use_web=use_web
            )

            return {
                "response": answer,
                "action": "reasoned_answer",
                "sources": {
                    "knowledge": len(entries),
                    "memory": len(memories),
                    "web": use_web,
                },
            }

        if intent == "command":

            return {
                "response": (
                    f"I understood the command: "
                    f"{content}"
                ),
                "action": "command",
            }

        if intent == "conversation":

            meaning = analyze_semantics(
                content
            )

            response = (
                self.semantic_response_builder.build(
                    content
                )
            )

            return {
                "response": response,
                "action": "semantic_conversation",
                "semantic": {
                    "subject": meaning.subject,
                    "relation": meaning.relation,
                    "object": meaning.object,
                    "meaning_type": meaning.meaning_type,
                    "confidence": meaning.confidence,
                },
            }

        return {
            "response": (
                "I don't know how to reason about "
                "that yet."
            ),
            "action": "unknown",
        }

    def _select_question_sources(
        self,
        question: str
    ):

        return self.answer_builder._select_knowledge(
            question
        )


reasoning_engine = ReasoningEngine()