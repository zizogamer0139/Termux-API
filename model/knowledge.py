from __future__ import annotations

from dataclasses import dataclass


@dataclass
class KnowledgeEntry:
    topic: str
    content: str
    keywords: list[str]


class KnowledgeBase:

    def __init__(self):

        self.entries: list[KnowledgeEntry] = []

        self._load_default_knowledge()

    def _load_default_knowledge(self) -> None:

        self.add(
            "termux",
            "Termux is an Android terminal application and Linux environment.",
            [
                "termux",
                "android terminal",
                "linux android",
            ],
        )

        self.add(
            "python",
            "Python is a general-purpose programming language known for readable syntax and a large ecosystem.",
            [
                "python",
                "programming",
                "language",
            ],
        )

        self.add(
            "minecraft",
            "Minecraft is a sandbox game where players can explore, build, survive, and create custom content.",
            [
                "minecraft",
                "block game",
                "sandbox game",
            ],
        )

        self.add(
            "sodium",
            "Sodium is a Minecraft optimization mod designed to improve rendering performance.",
            [
                "sodium",
                "minecraft optimization",
                "rendering",
            ],
        )

    def add(
        self,
        topic: str,
        content: str,
        keywords: list[str],
    ) -> None:

        self.entries.append(
            KnowledgeEntry(
                topic=topic,
                content=content,
                keywords=keywords,
            )
        )

    def search(
        self,
        query: str,
    ) -> list[KnowledgeEntry]:

        query = query.lower().strip()

        if not query:
            return []

        results = []

        for entry in self.entries:

            score = 0

            if entry.topic.lower() in query:
                score += 3

            for keyword in entry.keywords:

                if keyword.lower() in query:
                    score += 2

            if score > 0:
                results.append(
                    (score, entry)
                )

        results.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return [
            entry
            for _, entry in results
        ]

    def get_best(
        self,
        query: str,
    ) -> KnowledgeEntry | None:

        results = self.search(query)

        if not results:
            return None

        return results[0]


knowledge = KnowledgeBase()